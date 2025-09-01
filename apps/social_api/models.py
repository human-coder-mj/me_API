from django.db import models
from profile_api.models import Profile


class SocialLink(models.Model):
    """
    Social media and professional links
    """
    LINK_TYPES = [
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('website', 'Personal Website'),
        ('portfolio', 'Portfolio'),
        ('blog', 'Blog'),
        ('other', 'Other'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='social_links')
    link_type = models.CharField(max_length=20, choices=LINK_TYPES)
    url = models.URLField()
    display_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.get_link_type_display()}: {self.url}"

    class Meta:
        verbose_name = 'Social Link'
        verbose_name_plural = 'Social Links'
        unique_together = ['profile', 'link_type']
