import uuid

import requests
import datetime

from apps.tournaments.models import Tournament
from apps.utils.db_queries import collect_first_timer_teams
from core.celery import app
from django.core.cache import cache
from core.settings import BASE_URL

@app.task()
def generate_tournaments():
    guid = str(uuid.uuid4())
    print("Task Ran Yay")
    cache.set(guid, True, timeout=30)

    base_url = f"{BASE_URL}api/tournament/start/"

    results = []
    tournaments = Tournament.objects.filter(start_date=datetime.date.today() - datetime.timedelta(days=1))
    if not tournaments.exists():
        return "No Tournaments found"

    for tournament in tournaments:
        url = f"{base_url}{tournament.slug}/"
        headers = {"X-GUID": guid}
        response = requests.get(url, headers=headers)

        if response.status_code == 201:
            results.append(f"OK: {tournament.slug}")
            teams_for_first_time_achievement = collect_first_timer_teams(tournament)

        else:
            results.append(f"FAIL: {tournament.slug} ({response.status_code})")

    return results

