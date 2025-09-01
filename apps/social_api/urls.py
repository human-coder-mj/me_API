from django.urls import path
from . import views

urlpatterns = [
    # Social link CRUD endpoints
    path('social/', views.SocialLinkListCreateView.as_view(), name='social-link-list-create'),
    path('social/<int:pk>/', views.SocialLinkDetailView.as_view(), name='social-link-detail'),
    
    # Name-based access
    path('social/profile/<str:name>/', views.social_links_by_profile_name, name='social-links-by-profile-name'),
    
    # Type-based filtering
    path('social/type/<str:link_type>/', views.social_links_by_type, name='social-links-by-type'),
    
    # Grouped data
    path('social/grouped/', views.social_links_grouped_by_type, name='social-links-grouped-by-type'),
    
    # Professional vs social distinction
    path('social/professional/', views.professional_links, name='professional-links'),
    path('social/social-media/', views.social_media_links, name='social-media-links'),
    
    # Statistics
    path('social/stats/', views.social_stats, name='social-stats'),
]
