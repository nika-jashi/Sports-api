from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.tournaments.models import Match
from apps.utils.generate_elimination import progress_round
from core.mongo_client import mongo


@receiver(pre_save, sender=Match)
def update_league_matches(sender, instance, **kwargs):
    if not instance.pk:
        print('Match is being created (no primary key yet)')
        return
    try:
        old_instance = Match.objects.get(pk=instance.pk)
        if old_instance.tournament.format != 'league':
            return
        print('Match fetched for comparison')
    except Match.DoesNotExist:
        print('Match not found in DB, treating as new')
        return

    if (old_instance.home_score != instance.home_score or
            old_instance.away_score != instance.away_score):
        standings = mongo("standings").find_one({"tournament_id": old_instance.tournament.id})

        if instance.home_score > instance.away_score:
            for standing in standings['standings']:
                if standing['team'] == old_instance.home_team.name:
                    standing['points'] += 3
                    standing['wins'] += 1
                if standing['team'] == old_instance.away_team.name:
                    standing['losses'] += 1
        if instance.home_score < instance.away_score:
            for standing in standings['standings']:
                if standing['team'] == old_instance.home_team.name:
                    standing['losses'] += 1
                if standing['team'] == old_instance.away_team.name:
                    standing['points'] += 3
                    standing['wins'] += 1
        if instance.home_score == instance.away_score:
            for standing in standings['standings']:
                if standing['team'] == old_instance.home_team.name:
                    standing['points'] += 1
                    standing['draws'] += 1
                if standing['team'] == old_instance.away_team.name:
                    standing['draws'] += 1
                    standing['points'] += 1

        mongo("standings").update_one(
            {"tournament_id": old_instance.tournament.id},
            {"$set": {"standings": standings['standings']}}
        )
    else:
        print('Match score unchanged')


@receiver(post_save, sender=Match)
def auto_progress_bracket(sender, instance, **kwargs):
    """
    Runs when a Match is saved.
    If all matches in the current stage are completed → create next round matches.
    """
    tournament = instance.tournament

    round_matches = Match.objects.filter(
        tournament=tournament,
        round_number=instance.round_number
    )

    if round_matches.exclude(match_status='completed').exists():
        return

    progress_round(tournament)