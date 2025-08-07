from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.tournaments.models import Match
from core.mongo_client import mongo


@receiver(pre_save, sender=Match)
def update_matches(sender, instance, **kwargs):
    if not instance.pk:
        print('Match is being created (no primary key yet)')
        return
    try:
        old_instance = Match.objects.get(pk=instance.pk)
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