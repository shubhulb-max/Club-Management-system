from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema
from django.db import transaction
from .models import MembershipLeave, Player, RegistrationRequest
from .serializers import MembershipLeaveSerializer, PlayerSerializer
from .auth_serializers import (
    ApproveRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    RegistrationRequestSerializer,
)
from teams.models import Team
from teams.serializers import TeamSerializer
from matches.models import Match
from matches.serializers import MatchSerializer
from financials.models import Transaction
from financials.serializers import TransactionSerializer
from media_gallery.models import Media
from media_gallery.serializers import MediaSerializer

User = get_user_model()

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: None})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone_number']

        if User.objects.filter(phone_number=phone).exists():
            return Response(
                {"error": "Account with this phone number already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        registration = serializer.save()

        return Response({
            "message": "Registration submitted for admin approval.",
            "status": "pending_approval",
            "registration_id": registration.id,
            "phone_number": registration.phone_number,
        }, status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class RegistrationRequestListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        registrations = RegistrationRequest.objects.filter(status=RegistrationRequest.STATUS_PENDING)
        serializer = RegistrationRequestSerializer(registrations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApproveRegistrationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(request=ApproveRegistrationSerializer, responses={200: None})
    def post(self, request, registration_id):
        serializer = ApproveRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            registration = get_object_or_404(
                RegistrationRequest.objects.select_for_update(),
                id=registration_id,
            )

            if registration.status == RegistrationRequest.STATUS_APPROVED:
                return Response(
                    {"error": "Registration request is already approved."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if User.objects.filter(phone_number=registration.phone_number).exists():
                return Response(
                    {"error": "Account with this phone number already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            player = Player.objects.filter(phone_number=registration.phone_number).select_for_update().first()
            role = serializer.validated_data["role"]
            age = serializer.validated_data["age"]

            user = User.objects.create_user(
                phone_number=registration.phone_number,
                password=None,
                first_name=registration.first_name,
                last_name=registration.last_name,
            )
            user.password = registration.password_hash
            user.save(update_fields=["password"])

            if player:
                if player.user_id:
                    return Response(
                        {"error": "Player is already linked to a user."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                player.user = user
                player.first_name = registration.first_name
                player.last_name = registration.last_name
                if not player.role:
                    player.role = role
                if not player.age:
                    player.age = age
                player.save(update_fields=["user", "first_name", "last_name", "role", "age"])
            else:
                player = Player.objects.create(
                    user=user,
                    first_name=registration.first_name,
                    last_name=registration.last_name,
                    phone_number=registration.phone_number,
                    age=age,
                    role=role,
                )

            membership = getattr(player, "membership", None)
            if membership and membership.status != "active":
                membership.status = "active"
                membership.save(update_fields=["status"])

            registration.status = RegistrationRequest.STATUS_APPROVED
            registration.approved_at = timezone.now()
            registration.approved_by = request.user
            registration.save(update_fields=["status", "approved_at", "approved_by", "updated_at"])

        return Response(
            {
                "message": "Registration approved successfully.",
                "status": registration.status,
                "user_id": user.id,
                "player_id": player.id,
            },
            status=status.HTTP_200_OK,
        )


class RejectRegistrationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, registration_id):
        with transaction.atomic():
            registration = get_object_or_404(
                RegistrationRequest.objects.select_for_update(),
                id=registration_id,
            )

            if registration.status == RegistrationRequest.STATUS_APPROVED:
                return Response(
                    {"error": "Approved registration request cannot be rejected."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if registration.status == RegistrationRequest.STATUS_REJECTED:
                return Response(
                    {"error": "Registration request is already rejected."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            registration.status = RegistrationRequest.STATUS_REJECTED
            registration.approved_at = timezone.now()
            registration.approved_by = request.user
            registration.save(update_fields=["status", "approved_at", "approved_by", "updated_at"])

        return Response(
            {
                "message": "Registration rejected successfully.",
                "status": registration.status,
            },
            status=status.HTTP_200_OK,
        )

class PlayerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        player = getattr(request.user, "player", None)
        if not player:
            return Response({"error": "Player profile not found."}, status=status.HTTP_404_NOT_FOUND)
        player.sync_membership_status()

        teams = Team.objects.filter(players=player).distinct()
        upcoming_matches = Match.objects.filter(
            Q(team1__in=teams) | Q(team2__in=teams),
            date__gte=timezone.now()
        ).distinct().order_by("date")

        other_teams = Team.objects.exclude(id__in=teams.values_list("id", flat=True)).order_by("name")

        last_transaction = (
            Transaction.objects.filter(player=player)
            .order_by("-payment_date", "-due_date", "-id")
            .first()
        )

        membership_transaction = (
            Transaction.objects.filter(player=player, category="monthly", paid=False, waived=False)
            .order_by("due_date", "id")
            .first()
        )

        recent_media = Media.objects.filter(is_approved=True).order_by("-uploaded_at")[:10]

        profile_picture_url = None
        if player.profile_picture:
            profile_picture_url = request.build_absolute_uri(player.profile_picture.url)

        return Response({
            "player": PlayerSerializer(player).data,
            "profile_picture": profile_picture_url,
            "teams": TeamSerializer(teams, many=True).data,
            "other_teams": TeamSerializer(other_teams, many=True).data,
            "upcoming_matches": MatchSerializer(upcoming_matches, many=True).data,
            "last_transaction": TransactionSerializer(last_transaction).data if last_transaction else None,
            "membership_payment": {
                "required": bool(membership_transaction),
                "transaction": (
                    TransactionSerializer(membership_transaction).data
                    if membership_transaction else None
                )
            },
            "media": MediaSerializer(recent_media, many=True).data,
            "media_upload_endpoint": "/api/media/"
        }, status=status.HTTP_200_OK)


class MembershipLeaveListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, player_id):
        player = get_object_or_404(Player.objects.select_related("membership"), id=player_id)
        membership = getattr(player, "membership", None)
        if membership is None:
            return Response({"error": "Membership not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MembershipLeaveSerializer(membership.leave_periods.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=MembershipLeaveSerializer, responses={201: MembershipLeaveSerializer})
    def post(self, request, player_id):
        player = get_object_or_404(Player.objects.select_related("membership"), id=player_id)
        membership = getattr(player, "membership", None)
        if membership is None:
            return Response({"error": "Membership not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MembershipLeaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_period = serializer.save(membership=membership)
        return Response(MembershipLeaveSerializer(leave_period).data, status=status.HTTP_201_CREATED)


class MembershipLeaveDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, leave_id):
        return get_object_or_404(
            MembershipLeave.objects.select_related("membership", "membership__player"),
            id=leave_id,
        )

    def patch(self, request, leave_id):
        leave_period = self.get_object(leave_id)
        serializer = MembershipLeaveSerializer(leave_period, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, leave_id):
        leave_period = self.get_object(leave_id)
        leave_period.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
