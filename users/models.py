from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta

# Keep your existing Status model exactly as is
class Status(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='status_images/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.timestamp + timedelta(hours=24)
    
    def __str__(self):
        return f"{self.user.username}'s Status"

# --- NEW PROFILE MODEL ---
class Profile(models.Model):
    PRONOUN_CHOICES = [
        ('', 'Prefer not to say'),
        ('he', 'He/Him'),
        ('she', 'She/Her'),
        ('they', 'They/Them'),
        ('other', 'Other pronouns')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )
    bio = models.CharField(
        max_length=250,
        blank=True,
        help_text="Max 250 characters"
    )
    display_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional different name to display"
    )
    location = models.CharField(
        max_length=100,
        blank=True
    )
    pronouns = models.CharField(
        max_length=20,
        choices=PRONOUN_CHOICES,
        blank=True
    )
    last_updated = models.DateTimeField(auto_now=True)

    last_activity = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s Profile"