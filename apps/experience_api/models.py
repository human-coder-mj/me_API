from django.db import models
from profile_api.models import Profile


class WorkExperience(models.Model):
    """
    Work experience details
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='work_experiences')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    achievements = models.TextField(blank=True)

    def __str__(self):
        return f"{self.position} at {self.company}"

    class Meta:
        verbose_name = 'Work Experience'
        verbose_name_plural = 'Work Experiences'
        ordering = ['-start_date']