import os
import random
import string
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework.exceptions import ValidationError

from apps.users.models import CustomUser


def tournament_picture_file_path(instance, filename):
    """ Generate file path for users profile picture """
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'users', filename)


class Tournament(models.Model):
    """ Model For Tournaments """

    TOURNAMENT_TYPE_CHOICES = [
        ('league', 'League'),
        ('single_elimination', 'Single Elimination'),
        ('double_elimination', 'Double Elimination'),
    ]

    TEAM_SIZES = [
        ('1', 'Individuals'),
        ('2', 'Two'),
        ('3', 'Three'),
        ('4', 'Four'),
        ('5', 'Five'),
        ('6', 'Six'),
        ('7', 'Seven'),
        ('8', 'Eight'),
        ('9', 'Nine'),
        ('10', 'Ten'),
        ('11', 'Eleven'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    format = models.CharField(max_length=20, choices=TOURNAMENT_TYPE_CHOICES)
    team_size = models.CharField(max_length=20, choices=TEAM_SIZES)
    tournament_image = models.ImageField(upload_to=tournament_picture_file_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    number_of_participants = models.IntegerField(default=2, validators=[
        MaxValueValidator(32),
        MinValueValidator(2)
    ])
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'Tournaments'

    def save(self, *args, **kwargs):
        self.slug = self.name.replace(' ', '') + ''.join(random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, k=12))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Team(models.Model):
    """ Model For Team Leader Who Created The Team """

    name = models.CharField(max_length=255)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="teams")
    leader = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'Team'
        unique_together = ('name', 'tournament')  # Ensures uniqueness within a tournament

    def clean(self):
        """ Ensure team name is unique only among active teams in the same tournament. """
        if Team.objects.filter(
                name=self.name, tournament=self.tournament, is_active=True
        ).exclude(id=self.id).exists():
            raise ValidationError(f"A team with the name '{self.name}' already exists in this tournament.")

    def save(self, *args, **kwargs):
        self.clean()
        if self.tournament.team_size == '1':
            self.name = self.leader.get_full_name()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """ Model For Team who Participates """

    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('member', 'team')
        db_table = 'TeamMembers'

    def __str__(self):
        return f"{self.team.name} - {self.member.get_full_name()}"


class Match(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="matches")
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    match_date = models.DateTimeField(null=True, blank=True)
    match_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="scheduled")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('tournament', 'home_team', 'away_team')

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.match_status}"