from django.urls import path

from apps.tournaments.views import (
    TournamentCreationView, TournamentDetailsView,TeamCreationView,TeamMembersAdditionView
)

app_name = 'tournament'

urlpatterns = [
    path('create/', TournamentCreationView.as_view(), name='create'),
    path('details/<str:slug>/', TournamentDetailsView.as_view(), name='details'),
    path('<str:tournament>/team/create/', TeamCreationView.as_view(), name='team-create'),
    path('team/<int:team_id>/team-member/add', TeamMembersAdditionView.as_view(), name='team-member-add'),
]