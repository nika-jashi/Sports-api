from django.urls import path

from apps.tournaments.views import (
    TournamentCreationView,
    TournamentDetailsView,
    TeamCreationView,
    TeamMembersAdditionView,
    ShowTeamDetailsView,
    TournamentStartView,
    AllTournamentView
)

app_name = 'tournament'

urlpatterns = [
    path('all/', AllTournamentView.as_view(), name='all'),
    path('create/', TournamentCreationView.as_view(), name='create'),
    path('details/<str:slug>/', TournamentDetailsView.as_view(), name='details'),
    path('start/<str:slug>/', TournamentStartView.as_view(), name='start'),
    path('<str:tournament>/team/create/', TeamCreationView.as_view(), name='team-create'),
    path('team/<int:team_id>/team-member/add', TeamMembersAdditionView.as_view(), name='team-member-add'),
    path('team/<int:team_id>/details/', ShowTeamDetailsView.as_view(), name='team-details'),
]
