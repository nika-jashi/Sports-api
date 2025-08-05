from apps.tournaments.models import Tournament


def initialize_standings(tournament: Tournament):
    standings_data = {
        "updated_at": "2025-09-05T16:30:00Z",
        "standings": [team for team in tournament.teams]
    }
