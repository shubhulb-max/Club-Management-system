from django.views.generic import ListView, DetailView
from .models import Player

class PlayerListView(ListView):
    model = Player
    template_name = 'players/player_list.html'
    context_object_name = 'players'

class PlayerDetailView(DetailView):
    model = Player
    template_name = 'players/player_detail.html'
    context_object_name = 'player'
