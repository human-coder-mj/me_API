from django.urls import path
from . import views

app_name = 'profile_api'

urlpatterns = [
    # API Documentation
    path('', views.api_documentation, name='api-documentation'),

    # Basic Profile CRUD operations
    path('profiles/', views.ProfileListCreateView.as_view(), name='profile-list-create'),
    path('profiles/<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),

    # Profile by name endpoints (main requirement)
    path('profile/<str:name>/', views.comprehensive_profile_by_name, name='profile-by-name'),

    # Statistics
    path('stats/', views.ProfileStatsView.as_view(), name='profile-stats'),
]
