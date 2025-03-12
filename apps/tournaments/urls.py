from django.urls import path

from apps.tournaments.views import (
    TournamentCreationView,
)

app_name = 'tournament'

urlpatterns = [
    path('create/', TournamentCreationView.as_view(), name='create'),
]