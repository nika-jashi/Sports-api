import os
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


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
    description = models.TextField(blank=True, null=True)
    format = models.CharField(max_length=20, choices=TOURNAMENT_TYPE_CHOICES)
    team_size = models.CharField(max_length=20, choices=TEAM_SIZES)
    tournament_image = models.ImageField(upload_to=tournament_picture_file_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    number_of_participants = models.IntegerField(default=2,validators=[
            MaxValueValidator(32),
            MinValueValidator(2)
        ])

    class Meta:
        db_table = 'Tournaments'

    def __str__(self):
        return self.name
