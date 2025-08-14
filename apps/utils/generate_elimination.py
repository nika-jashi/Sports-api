from random import shuffle

from django.db import transaction
from django.db.models import Max
from apps.tournaments.models import Match
from apps.tournaments.serializers import MatchSerializer

def generate_eliminations(league_teams_data):
    shuffle(league_teams_data)

    matches = []
    counter = 1

    # Group teams into pairs (2 per match)
    for i in range(0, len(league_teams_data), 2):
        team1 = league_teams_data[i]
        team2 = league_teams_data[i + 1] if i + 1 < len(league_teams_data) else None  # Handle odd count

        matches.append({
            'home': team1,
            'away': team2,
            'match_number': counter,
        })
        counter += 1
    return matches


def get_winner(match):
    if match.home_score is None or match.away_score is None:
        return None
    if match.home_score == match.away_score:
        return None
    return match.home_team if match.home_score > match.away_score else match.away_team

def progress_round(tournament):
    """
    Progresses the current round of the tournament by creating next round matches.
    Uses MatchSerializer for creation.
    """

    # Get the current round number
    max_round = Match.objects.filter(tournament=tournament).aggregate(Max('round_number'))['round_number__max']
    if max_round is None:
        max_round = 1

    # Get matches only from current round
    current_round_matches = list(
        Match.objects.filter(tournament=tournament, round_number=max_round).order_by('match_number')
    )
    if len(current_round_matches) == 1:
        return []
    if not current_round_matches:
        return []

    # Check if all matches are completed
    if any(m.match_status != 'completed' for m in current_round_matches):
        return []

    # Build winners list
    winners = []
    for m in current_round_matches:
        winner = get_winner(m)
        if winner is None:
            return []  # no clear winner → stop progression
        winners.append(winner)

    if len(winners) % 2 != 0:
        raise ValueError("Current round must have an even number of matches for progression.")

    half = len(winners) // 2

    # Find next available match_number
    max_match_num = Match.objects.filter(tournament=tournament).aggregate(Max('match_number'))['match_number__max'] or 0
    next_match_number = max_match_num

    created = []
    with transaction.atomic():
        # Avoid creating if next round already exists
        if Match.objects.filter(tournament=tournament, round_number=max_round + 1).exists():
            return []

        for i in range(half):
            home_team = winners[i]
            away_team = winners[i + half]
            next_match_number += 1

            if Match.objects.filter(
                tournament=tournament,
                round_number=max_round + 1,
                home_team=home_team,
                away_team=away_team,
            ).exists():
                continue

            match_data = {
                'tournament': tournament,
                'round_number': max_round + 1,
                'match_number': next_match_number,
                'home_team': home_team,
                'away_team': away_team,
            }

            serializer = MatchSerializer(data=match_data, context={'match_data': match_data})
            if serializer.is_valid(raise_exception=True):
                created_match = serializer.save()
                created.append(created_match)

    return created