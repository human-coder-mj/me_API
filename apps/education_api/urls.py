from django.urls import path
from . import views

app_name = 'education_api'

urlpatterns = [
    # Basic Education CRUD operations
    path('education/', views.EducationListCreateView.as_view(), name='education-list-create'),
    path('education/<int:pk>/', views.EducationDetailView.as_view(), name='education-detail'),
    
    # Education by profile
    path('education/profile/<int:profile_id>/', views.education_by_profile, name='education-by-profile'),
    path('education/profile/<str:name>/', views.education_by_profile_name, name='education-by-profile-name'),
    
    # Reference data endpoints
    path('education/institutions/', views.education_institutions, name='education-institutions'),
    path('education/degrees/', views.education_degrees, name='education-degrees'),
    
    # Search functionality
    path('education/search/', views.education_search, name='education-search'),
    
    # Statistics
    path('education/stats/', views.EducationStatsView.as_view(), name='education-stats'),
]
