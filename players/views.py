from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema
from .models import Player
from .serializers import PlayerSerializer
from .auth_serializers import RegisterSerializer, LoginSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: None})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')

        # Check if user already exists
        if User.objects.filter(username=phone_number).exists():
            return Response({"error": "Account with this phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Check for existing player profile
        players = Player.objects.filter(phone_number=phone_number)
        player = None

        if players.exists():
            # Claim existing profile
            if players.count() > 1:
                return Response({"error": "Multiple profiles found. Contact support."}, status=status.HTTP_409_CONFLICT)

            player = players.first()
            if player.user:
                 return Response({"error": "This player profile is already linked to a user."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Create new profile
            if not first_name or not last_name:
                return Response({"error": "First name and last name are required for new registrations."}, status=status.HTTP_400_BAD_REQUEST)

            player = Player.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                age=0, # Default or require age? Let's default to 0 for now or user can update later
                role='all_rounder' # Default role
            )

        try:
            user = User.objects.create_user(username=phone_number, password=password)
            player.user = user
            player.save()

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "message": "Registration successful.",
                "token": token.key,
                "user_id": user.id,
                "player_id": player.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Registration failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: None})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']

        user = authenticate(username=phone_number, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            player_id = user.player.id if hasattr(user, 'player') else None
            return Response({
                "token": token.key,
                "user_id": user.id,
                "player_id": player_id
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
