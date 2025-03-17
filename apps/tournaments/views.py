from typing import List
import json

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tournaments.models import Tournament, Team, TeamMember
from apps.tournaments.serializers import TournamentSerializer, TeamSerializer, TeamMemberSerializer, MatchSerializer
from apps.users.models import CustomUser
from apps.utils.generate_league import generate_unique_matches


@extend_schema(tags=["Tournament"],
               responses={
                   status.HTTP_201_CREATED: TournamentSerializer,
                   status.HTTP_400_BAD_REQUEST: TournamentSerializer,
               })
class TournamentCreationView(APIView):
    """ View For Creating Tournaments """
    serializer_class = TournamentSerializer

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(creator=request.user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Tournament"])
class TournamentDetailsView(APIView):
    """ View For User To See Tournaments """

    serializer_class = TournamentSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, slug, *args, **kwargs) -> Response:
        """ GET Method FFor User To See Tournaments """

        current_tournament = Tournament.objects.filter(slug=slug).first()
        serializer = TournamentSerializer(instance=current_tournament)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, slug, *args, **kwargs) -> Response:
        """ PATCH Method For Users To Update Their Tournaments """

        current_tournament = Tournament.objects.filter(slug=slug).first()
        serializer = TournamentSerializer(instance=current_tournament, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Teams"],
               responses={
                   status.HTTP_201_CREATED: TeamSerializer,
                   status.HTTP_400_BAD_REQUEST: TeamSerializer,
               })
class TeamCreationView(APIView):
    """ View For Creating Team With A Leader """
    serializer_class = TeamSerializer

    permission_classes = (IsAuthenticated,)

    def post(self, request, tournament, *args, **kwargs) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            current_tournament = Tournament.objects.filter(slug=tournament).first()
            serializer.save(leader=request.user, tournament=current_tournament)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Teams"],
               responses={
                   status.HTTP_201_CREATED: TeamMemberSerializer,
                   status.HTTP_400_BAD_REQUEST: TeamMemberSerializer,
               })
class TeamMembersAdditionView(APIView):
    """ View For Adding Member In To The Team """
    serializer_class = TeamMemberSerializer

    permission_classes = (IsAuthenticated,)

    def post(self, request, team_id, *args, **kwargs) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            current_team = Team.objects.filter(id=team_id).first()
            serializer.save(member=request.user, team=current_team)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Teams"],
               responses={
                   status.HTTP_201_CREATED: TeamMemberSerializer,
                   status.HTTP_400_BAD_REQUEST: TeamMemberSerializer,
               })
class ShowTeamDetailsView(APIView):
    """ View For Showing Teams Details """

    permission_classes = (IsAuthenticated,)

    def get(self, request, team_id, *args, **kwargs) -> Response:
        current_team = Team.objects.filter(id=team_id).first()

        if not current_team:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)

        team_members = TeamMember.objects.filter(team=current_team).select_related("member")

        data = {
            'leader': {
                'id': current_team.leader.id,
                'first_name': current_team.leader.first_name,
                'last_name': current_team.leader.last_name,
                'email': current_team.leader.email,
            },
            'members': [
                {
                    'id': member.member.id,
                    'first_name': member.member.first_name,
                    'last_name': member.member.last_name,
                    'email': member.member.email
                }
                for member in team_members
            ],
        }
        return Response(data, status=status.HTTP_200_OK, content_type='application/json')


@extend_schema(tags=["Teams"],
               responses={
                   status.HTTP_201_CREATED: TeamMemberSerializer,
                   status.HTTP_400_BAD_REQUEST: TeamMemberSerializer,
               })
class TeamMembersAdditionView(APIView):
    """ View For Removing Member From The Team """

    permission_classes = (IsAuthenticated,)

    def post(self, request, team_id, member_id, *args, **kwargs) -> Response:
        current_team = Team.objects.filter(leader=request.user, id=team_id).first()
        if current_team.leader is not None and current_team.is_active:
            TeamMember.objects.filter(team=current_team, member_id=member_id).first().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Tournament"])
class TournamentStartView(APIView):
    """ View For Starting A Tournament """

    serializer_class = MatchSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug, *args, **kwargs) -> Response:
        """ Start a tournament by generating and saving matches """

        current_tournament = get_object_or_404(Tournament, slug=slug)

        teams = list(Team.objects.filter(tournament=current_tournament))

        if len(teams) < 2:
            return Response({"error": "At least two teams are required to start a tournament."},
                            status=status.HTTP_400_BAD_REQUEST)

        matches = generate_unique_matches(league_teams_data=teams)

        print(f"Generated Matches: {matches}")

        created_matches = []
        for match in matches:
            match_data = {
                'tournament': current_tournament,
                'home_team': match['home'],
                'away_team': match['away'],
            }
            serializer = self.serializer_class(data=match_data,context={'match_data': match_data})

            if serializer.is_valid():
                saved_match = serializer.save()
                created_matches.append(saved_match)
            else:
                print(serializer.errors)

        return Response(
            {"message": "Tournament started successfully!", "matches_created": len(created_matches)},
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=["Tournament"])
class AllTournamentView(APIView):
    """ View To Get All Tournaments """

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs) -> Response:
        tournaments = Tournament.objects.all().order_by('-created_at')
        all_tournaments = TournamentSerializer(instance=tournaments, many=True)
        return Response(data=all_tournaments.data, status=status.HTTP_200_OK)
