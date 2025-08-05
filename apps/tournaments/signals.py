from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.tournaments.models import Match


@receiver(pre_save, sender=Match)
def update_matches(sender, instance, **kwargs):
    # Check if instance exists in DB (i.e., update, not create)
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

        print(f"Score changed for match {instance}:")
        print(f"Old: {old_instance.home_score}-{old_instance.away_score}")
        print(f"New: {instance.home_score}-{instance.away_score}")
    else:
        print('Match score unchanged')