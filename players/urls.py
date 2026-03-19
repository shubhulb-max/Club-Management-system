from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ApproveRegistrationView,
    LoginView,
    MembershipLeaveDetailView,
    MembershipLeaveListCreateView,
    PlayerDashboardView,
    RejectRegistrationView,
    RegisterView,
    RegistrationRequestListView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('registrations/', RegistrationRequestListView.as_view(), name='registration-list'),
    path('registrations/<int:registration_id>/approve/', ApproveRegistrationView.as_view(), name='registration-approve'),
    path('registrations/<int:registration_id>/reject/', RejectRegistrationView.as_view(), name='registration-reject'),
    path('dashboard/', PlayerDashboardView.as_view(), name='player-dashboard'),
    path('players/<int:player_id>/membership-leaves/', MembershipLeaveListCreateView.as_view(), name='membership-leave-list-create'),
    path('membership-leaves/<int:leave_id>/', MembershipLeaveDetailView.as_view(), name='membership-leave-detail'),
]
