from django.urls import path
from .views import RegisterView, LoginView, PlayerDashboardView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('dashboard/', PlayerDashboardView.as_view(), name='player-dashboard'),
]
