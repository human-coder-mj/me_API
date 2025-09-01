from django.urls import path
from . import views

app_name = 'profile_api'

urlpatterns = [
    # API Documentation
    path('', views.api_documentation, name='api-documentation'),

    # Basic Profile CRUD operations
    path('profiles/', views.ProfileListCreateView.as_view(), name='profile-list-create'),
    path('profiles/<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),

    # Comprehensive profile with all related data
    path('profiles/<int:pk>/comprehensive/', views.ComprehensiveProfileView.as_view(), name='profile-comprehensive'),

    # Profile by email endpoints
    path('profiles/email/<str:email>/', views.profile_by_email, name='profile-by-email'),
    path('profiles/email/<str:email>/comprehensive/', views.comprehensive_profile_by_email, name='comprehensive-profile-by-email'),

    # Query endpoints as per requirements
    path('projects/', views.projects_by_skill, name='projects-by-skill'),  # GET /projects?skill=python
    path('skills/top/', views.top_skills, name='top-skills'),  # GET /skills/top
    path('search/', views.search_profiles, name='search-profiles'),  # GET /search?q=...

    # Statistics
    path('stats/', views.ProfileStatsView.as_view(), name='profile-stats'),
]
