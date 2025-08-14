import json

from bson import json_util
from django.db.models import QuerySet

from apps.tournaments.models import Tournament
from apps.users.models import CustomUser, Achievement
from core.mongo_client import mongo


def check_user_exists(uid=None, email=None, username=None) -> bool:
    queryset = CustomUser.objects.filter(is_active=True)

    return (
        queryset.filter(id=uid).exists() if uid is not None else
        queryset.filter(email=email).exists() if email is not None else
        queryset.filter(username=username).exists() if username is not None else
        False
    )


def check_if_user_is_active(email) -> bool:
    user = CustomUser.objects.get(email=email)
    return user.is_active


def collect_first_timer_teams(tournament: Tournament) -> dict:
    current_members = CustomUser.objects.filter(
        teammember__team__tournament=tournament
    ).distinct()

    first_timers = current_members.exclude(
        teammember__team__tournament__in=Tournament.objects.exclude(pk=tournament.pk)
    )

    return {user.id: user.email for user in first_timers}

def get_all_current_users_achievements(user_id:int) -> dict:
    achievements = {
        'user': user_id,
        'total_points': 0,
        'achievements': [

        ],
    }
    achievements_queryset = mongo("achievements").find({"user_id": user_id})
    for achievement in json.loads(json_util.dumps(achievements_queryset)):
        users_achievements = Achievement.objects.get(slug_code=achievement['achievement_id'])
        achievements['achievements'].append({
            "slug_code": users_achievements.slug_code,
            "title": users_achievements.title,
            "description": users_achievements.description,
            "points": users_achievements.points,
            "date_achieved": achievement['date_achieved'],
        }),
        achievements['total_points'] += users_achievements.points
    return achievements