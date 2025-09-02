from django.urls import path
from . import views

urlpatterns = [
    # Name-based access
    path('profile/<str:name>/experience/', views.experience_by_profile_name, name='experience-by-profile-name'),
    
    # Statistics
    path('experience/stats/', views.experience_stats, name='experience-stats'),
]
