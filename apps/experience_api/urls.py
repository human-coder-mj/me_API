from django.urls import path
from . import views

urlpatterns = [
    # Work experience CRUD endpoints
    path('experience/', views.WorkExperienceListCreateView.as_view(), name='experience-list-create'),
    path('experience/<int:pk>/', views.WorkExperienceDetailView.as_view(), name='experience-detail'),
    
    # Name-based access
    path('experience/profile/<str:name>/', views.experience_by_profile_name, name='experience-by-profile-name'),
    
    # Statistics
    path('experience/stats/', views.experience_stats, name='experience-stats'),
]
