from django.urls import path
from .views import MatchListView, MatchDetailView

urlpatterns = [
    path('', MatchListView.as_view(), name='match_list'),
    path('<int:pk>/', MatchDetailView.as_view(), name='match_detail'),
]
