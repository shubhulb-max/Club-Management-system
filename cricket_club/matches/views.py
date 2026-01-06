from django.views.generic import ListView, DetailView
from .models import Match

class MatchListView(ListView):
    model = Match
    template_name = 'matches/match_list.html'
    context_object_name = 'matches'

class MatchDetailView(DetailView):
    model = Match
    template_name = 'matches/match_detail.html'
    context_object_name = 'match'
