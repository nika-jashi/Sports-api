from apps.tournaments.models import Tournament
from apps.users.models import CustomUser, Achievement


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
