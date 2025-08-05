from pymongo import MongoClient

client = MongoClient("mongodb://mongodb:27017/")
db = client["sports_api"]

def get_collection(name):
    return db[name]


def save_standings(tournament_id: int, data: dict):
    collection = get_collection("standings")

    # Upsert (update or insert)
    collection.replace_one(
        {"tournament_id": tournament_id},
        {"tournament_id": tournament_id, **data},
        upsert=True
    )

standings_data = {
    "updated_at": "2025-09-05T16:30:00Z",
    "standings": [
        {"team": "Team C", "points": 44, "wins": 11, "draws": 6, "losses": 1},
        {"team": "Team D", "points": 5, "wins": 1, "draws": 2, "losses": 19},
    ]
}

save_standings(tournament_id=102, data=standings_data)