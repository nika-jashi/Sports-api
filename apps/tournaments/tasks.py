import uuid

import requests
import datetime

from apps.tournaments.models import Tournament
from core.celery_app import app
from django.core.cache import cache
from core.settings import BASE_URL

@app.task()
def generate_tournaments():
    guid = str(uuid.uuid4())

    cache.set(guid, True, timeout=30)

    base_url = f"{BASE_URL}api/tournament/start/"

    for tournament in Tournament.objects.filter(start_date=datetime.date.today() - datetime.timedelta(days=1)).all():
        url = f"{base_url + tournament.slug}/"

        headers = {"X-GUID": guid}
        response = requests.get(url, headers=headers)

        # Log the response
        if response.status_code == 201:
            return f"API call successful: {response.json()}"
        else:
            return f"API call failed: {response.status_code} - {response.text}"
    return "No Tournaments found"
