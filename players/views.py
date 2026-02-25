from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema
from django.db import transaction
from .models import Player
from .serializers import PlayerSerializer
from .auth_serializers import RegisterSerializer, LoginSerializer
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

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: None})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')

        with transaction.atomic():
            # 1️⃣ Prevent duplicate users
            if User.objects.filter(phone_number=phone).exists():
                return Response(
                    {"error": "Account with this phone number already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2️⃣ Look for existing Player (admin-created)
            player = Player.objects.filter(phone_number=phone).select_for_update().first()

            # 3️⃣ Create user
            user = User.objects.create_user(
                phone_number=phone,
                password=password,
                first_name=first_name or (player.first_name if player else ""),
                last_name=last_name or (player.last_name if player else ""),
            )

            # 4️⃣ Link or create Player
            if player:
                if player.user:
                    raise ValueError("Player already linked to a user.")
                player.user = user
                player.save(update_fields=['user'])
            else:
                Player.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone,
                    age=0,
                    role='all_rounder'
                )

            token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Registration successful",
            "token": token.key,
            "user_id": user.id,
            "player_id": user.player.id,
            "role": "player"
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: None})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']

        user = authenticate(phone_number=phone_number, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            player_id = user.player.id if hasattr(user, 'player') else None
            return Response({
                "token": token.key,
                "user_id": user.id,
                "player_id": player_id,
                "role": "player",
                "dashboard_url": "/api/auth/dashboard/"
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

class PlayerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        player = getattr(request.user, "player", None)
        if not player:
            return Response({"error": "Player profile not found."}, status=status.HTTP_404_NOT_FOUND)

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
            Transaction.objects.filter(player=player, category="monthly", paid=False)
            .order_by("due_date", "id")
            .first()
        )

        recent_media = Media.objects.all().order_by("-uploaded_at")[:10]

        return Response({
            "player": PlayerSerializer(player).data,
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
