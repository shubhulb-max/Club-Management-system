from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Player
from .serializers import PlayerSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='claim-profile')
    def claim_profile(self, request):
        """
        Allows a user to claim a player profile using their phone number and set a password.
        Payload: { "phone_number": "...", "password": "...", "username": "..." (optional, defaults to phone) }
        """
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        username = request.data.get('username')

        if not phone_number or not password:
            return Response({"error": "Phone number and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Find the Player
        players = Player.objects.filter(phone_number=phone_number)

        if not players.exists():
            return Response({"error": "No player profile found with this phone number."}, status=status.HTTP_404_NOT_FOUND)

        if players.count() > 1:
            return Response({"error": "Multiple profiles found with this number. Please contact support."}, status=status.HTTP_409_CONFLICT)

        player = players.first()

        # 2. Check if already claimed
        if player.user:
            return Response({"error": "This profile is already linked to a user account."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Create User
        if not username:
            username = phone_number # Default username is the phone number

        if User.objects.filter(username=username).exists():
             return Response({"error": "Username already taken. Please choose another."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, password=password)

            # 4. Link User to Player
            player.user = user
            player.save()

            # 5. Generate Token for immediate login
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "message": "Profile claimed successfully.",
                "token": token.key,
                "user_id": user.id,
                "player_id": player.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Failed to create account: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
