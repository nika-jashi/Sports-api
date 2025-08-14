import os
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)


class CustomUserManager(BaseUserManager):
    """ Manager For User """

    def create_user(self, email, password, **extra_fields):
        """ Create and save a User with the given email and password. """

        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        """ Create and save a SuperUser with the given email and password. """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is False:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is False:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


def profile_picture_file_path(instance, filename):
    """ Generate file path for users profile picture """
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'users', filename)


class CustomUser(AbstractUser):
    """ User In The System """

    email = models.EmailField(
        max_length=255,
        unique=True,
        error_messages={'unique': 'Email Already Exists'})
    username = None
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        db_table = 'Users'

    def __str__(self):
        return self.email


class CustomUserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to=profile_picture_file_path, null=True)

    GENDER_CHOICES = (
        ('U', _('Unknown')),
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Others')),
    )
    gender = models.CharField(
        choices=GENDER_CHOICES,
        default='U',  # Start with U (Unknown)
        null=True,
    )

    class Meta:
        db_table = 'UserProfiles'

    def __str__(self):
        return f"{self.user.email}'s Profile"


def achievement_icon_upload_path(instance, filename):
    """Generate file path for achievement icons"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"uploads/achievements/{filename}"


class Achievement(models.Model):
    """Static achievement template"""
    CATEGORY_CHOICES = [
        ('tournament', 'Tournament'),
        ('match', 'Match'),
        ('team', 'Team'),
        ('personal', 'Personal'),
    ]

    slug_code = models.SlugField(
        max_length=50,
        unique=True,
        help_text="Unique code for internal reference (e.g., 'win_first_match')"
    )
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='personal')
    points = models.PositiveIntegerField(default=0)
    icon = models.ImageField(upload_to=achievement_icon_upload_path, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'Achievements'
        ordering = ['category', 'title']

    def __str__(self):
        return f"{self.title} ({self.slug_code})"