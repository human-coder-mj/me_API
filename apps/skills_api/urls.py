from django.urls import path
from . import views

urlpatterns = [
    # Skill CRUD endpoints
    path('skills/', views.SkillListCreateView.as_view(), name='skill-list-create'),
    path('skills/<int:pk>/', views.SkillDetailView.as_view(), name='skill-detail'),
    
    # Name-based access
    path('skills/profile/<str:name>/', views.skills_by_profile_name, name='skills-by-profile-name'),
    
    # Category-based filtering
    path('skills/category/<str:category>/', views.skills_by_category, name='skills-by-category'),
    
    # Level-based filtering
    path('skills/level/<str:level>/', views.skills_by_level, name='skills-by-level'),
    
    # Grouped data
    path('skills/grouped/', views.skills_grouped_by_category, name='skills-grouped-by-category'),
    
    # Statistics
    path('skills/stats/', views.skill_stats, name='skill-stats'),
]
