from django.db import models
from profile_api.models import Profile


class Skill(models.Model):
    """
    Skills associated with the profile
    """
    SKILL_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='intermediate')
    category = models.CharField(max_length=50, blank=True)  # e.g., Programming, Design, etc.

    def __str__(self):
        return f"{self.name} ({self.level})"

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
        unique_together = ['profile', 'name']
