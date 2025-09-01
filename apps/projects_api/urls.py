from django.urls import path
from . import views

urlpatterns = [
    # Project CRUD endpoints
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    
    # Name-based access
    path('projects/profile/<str:name>/', views.projects_by_profile_name, name='projects-by-profile-name'),
    
    # Featured projects
    path('projects/featured/', views.featured_projects, name='featured-projects'),
    
    # Technology-based filtering
    path('projects/technology/<str:technology>/', views.projects_by_technology, name='projects-by-technology'),
    
    # Statistics
    path('projects/stats/', views.project_stats, name='project-stats'),
]
