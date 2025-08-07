from django.urls import path

from apps.tournaments.views import (
    TournamentCreationView,
    TournamentDetailsView,
    TeamCreationView,
    TeamMembersAdditionView,
    ShowTeamDetailsView,
    TournamentStartView,
    AllTournamentView,
    ShowAllTeamsInTournament,
    UpdateMatchesView,
    TournamentStandingsView,
TournamentMatchesView,

)

app_name = 'tournament'

urlpatterns = [
    path('all/', AllTournamentView.as_view(), name='all'),
    path('create/', TournamentCreationView.as_view(), name='create'),
    path('details/<str:slug>/', TournamentDetailsView.as_view(), name='details'),
    path('start/<str:slug>/', TournamentStartView.as_view(), name='start'),
    path('<str:tournament>/team/create/', TeamCreationView.as_view(), name='team-create'),
    path('<str:tournament>/team/all', ShowAllTeamsInTournament.as_view(), name='all-teams-in-tournament'),
    path('team/<int:team_id>/team-member/add', TeamMembersAdditionView.as_view(), name='team-member-add'),
    path('team/<int:team_id>/details/', ShowTeamDetailsView.as_view(), name='team-details'),
    path('<str:tournament>/match/<int:match_pk>/update', UpdateMatchesView.as_view(), name='match-update'),
    path('<str:tournament>/standings/', TournamentStandingsView.as_view(), name='standings'),
    path('<str:tournament>/matches/all/', TournamentMatchesView.as_view(), name='all-matches'),
]
