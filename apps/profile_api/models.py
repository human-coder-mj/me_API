from django.db import models


class Profile(models.Model):
    """
    Main profile model containing personal information
    """
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self)->str:
        return str(self.name)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'