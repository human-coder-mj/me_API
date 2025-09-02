from django.urls import path
from . import views

app_name = 'education_api'

urlpatterns = [
    # Basic Education CRUD operations
    # Education by profile
    path('profile/<str:name>/education/', views.education_by_profile_name, name='education-by-profile-name'),
    
    # Search functionality
    path('education/search/', views.education_search, name='education-search'),
    
    # Statistics
    path('education/stats/', views.EducationStatsView.as_view(), name='education-stats'),
]
