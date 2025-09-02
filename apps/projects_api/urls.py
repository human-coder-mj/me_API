from django.urls import path
from . import views

urlpatterns = [
    # Project CRUD endpoints
    # Name-based access
    path('profile/<str:name>/projects', views.projects_by_profile_name, name='projects-by-profile-name'),
    
    # Featured projects
    path('projects/featured/', views.featured_projects, name='featured-projects'),

    # Enhanced skill-based filtering
    path('projects/', views.projects_by_skill, name='projects-by-skill'),  # GET /projects?skill=python&level=advanced
    
    # Statistics
    path('projects/stats/', views.project_stats, name='project-stats'),
]
