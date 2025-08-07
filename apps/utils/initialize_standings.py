from datetime import datetime
from apps.tournaments.models import Tournament
from core.mongo_client import mongo

def initialize_standings_for_league(tournament: Tournament):
    standings_data = {
        "tournament_id": tournament.id,
        "tournament_name": tournament.name,
        "tournament_date": str(tournament.start_date),
        "updated_at": str(datetime.now()),
        "standings": [{"team_id":team.id,"team":team.name,"points": 0, "wins": 0, "draws": 0, "losses": 0} for team in tournament.teams.all()]
    }
    mongo("standings").insert_one(
        standings_data
    )
