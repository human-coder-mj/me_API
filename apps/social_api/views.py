from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from collections import defaultdict
from profile_api.models import Profile
from profile_api.views import IsAdminUserOrReadOnly
from .models import SocialLink
from .serializers import (
    SocialLinkSerializer, 
    SocialLinkCreateSerializer, 
    SocialLinkSummarySerializer
)


class SocialLinkListCreateView(generics.ListCreateAPIView):
    """
    List all social links or create a new one
    GET: Public access
    POST: Admin only
    """
    queryset = SocialLink.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SocialLinkCreateSerializer
        return SocialLinkSerializer
    
    def get_queryset(self):
        """
        Filter social links by query parameters
        """
        queryset = SocialLink.objects.select_related('profile').all()
        
        # Filter by profile name
        profile_name = self.request.query_params.get('profile_name')
        if profile_name:
            queryset = queryset.filter(profile__name__icontains=profile_name)
        
        # Filter by link type
        link_type = self.request.query_params.get('link_type')
        if link_type:
            queryset = queryset.filter(link_type=link_type)
        
        # Filter by platform (case-insensitive link type search)
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(link_type__icontains=platform)
        
        # Search across multiple fields
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(display_name__icontains=search) |
                Q(url__icontains=search) |
                Q(link_type__icontains=search) |
                Q(profile__name__icontains=search)
            )
        
        # Get summary view
        summary = self.request.query_params.get('summary')
        if summary and summary.lower() == 'true':
            self.serializer_class = SocialLinkSummarySerializer
        
        return queryset


class SocialLinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a social link instance
    GET: Public access
    PUT/PATCH/DELETE: Admin only
    """
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer
    permission_classes = [IsAdminUserOrReadOnly]


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def social_links_by_profile_name(request, name):
    """
    Get all social links for a specific profile by name
    """
    try:
        profile = Profile.objects.get(name__iexact=name)
        links = SocialLink.objects.filter(profile=profile).order_by('link_type')
        
        # Check if summary view is requested
        summary = request.query_params.get('summary')
        if summary and summary.lower() == 'true':
            serializer = SocialLinkSummarySerializer(links, many=True)
        else:
            serializer = SocialLinkSerializer(links, many=True)
            
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response(
            {'error': f'Profile with name "{name}" not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def social_links_by_type(request, link_type):
    """
    Get all social links of a specific type
    """
    links = SocialLink.objects.filter(
        link_type=link_type
    ).select_related('profile').order_by('profile__name')
    
    # Check if summary view is requested
    summary = request.query_params.get('summary')
    if summary and summary.lower() == 'true':
        serializer = SocialLinkSummarySerializer(links, many=True)
    else:
        serializer = SocialLinkSerializer(links, many=True)
        
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def social_links_grouped_by_type(request):
    """
    Get social links grouped by type with statistics
    """
    links = SocialLink.objects.select_related('profile').order_by('link_type', 'profile__name')
    
    # Group links by type
    link_types = defaultdict(list)
    for link in links:
        link_types[link.link_type].append(link)
    
    # Build response data
    grouped_data = []
    for link_type, link_list in link_types.items():
        link_type_display = dict(SocialLink.LINK_TYPES).get(link_type, link_type.title())
        
        grouped_data.append({
            'link_type': link_type,
            'link_type_display': link_type_display,
            'links': SocialLinkSerializer(link_list, many=True).data,
            'link_count': len(link_list)
        })
    
    # Sort by link count descending
    grouped_data.sort(key=lambda x: x['link_count'], reverse=True)
    
    return Response(grouped_data)


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def professional_links(request):
    """
    Get professional social links (GitHub, LinkedIn, Portfolio)
    """
    professional_types = ['github', 'linkedin', 'portfolio', 'website']
    links = SocialLink.objects.filter(
        link_type__in=professional_types
    ).select_related('profile').order_by('link_type', 'profile__name')
    
    # Check if summary view is requested
    summary = request.query_params.get('summary')
    if summary and summary.lower() == 'true':
        serializer = SocialLinkSummarySerializer(links, many=True)
    else:
        serializer = SocialLinkSerializer(links, many=True)
        
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def social_media_links(request):
    """
    Get social media links (Twitter, etc.)
    """
    social_types = ['twitter', 'blog', 'other']
    links = SocialLink.objects.filter(
        link_type__in=social_types
    ).select_related('profile').order_by('link_type', 'profile__name')
    
    # Check if summary view is requested
    summary = request.query_params.get('summary')
    if summary and summary.lower() == 'true':
        serializer = SocialLinkSummarySerializer(links, many=True)
    else:
        serializer = SocialLinkSerializer(links, many=True)
        
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def social_stats(request):
    """
    Get comprehensive social link statistics
    """
    all_links = SocialLink.objects.select_related('profile')
    
    # Basic counts
    total_links = all_links.count()
    unique_link_types = all_links.values('link_type').distinct().count()
    profiles_with_links = all_links.values('profile').distinct().count()
    
    # Link type distribution
    link_type_distribution = {}
    for link_type_choice in SocialLink.LINK_TYPES:
        link_type_key = link_type_choice[0]
        link_type_display = link_type_choice[1]
        link_count = all_links.filter(link_type=link_type_key).count()
        link_type_distribution[link_type_display] = link_count
    
    # Most popular platforms
    platform_stats = all_links.values('link_type').annotate(
        count=Count('id'),
        profiles_count=Count('profile', distinct=True)
    ).order_by('-count')
    
    most_popular_platforms = []
    for stat in platform_stats:
        link_type_display = dict(SocialLink.LINK_TYPES).get(stat['link_type'], stat['link_type'].title())
        most_popular_platforms.append({
            'platform': link_type_display,
            'link_type': stat['link_type'],
            'total_links': stat['count'],
            'profiles_count': stat['profiles_count']
        })
    
    # Profiles by platform (which profiles use which platforms)
    profiles_by_platform = {}
    for link_type_choice in SocialLink.LINK_TYPES:
        link_type_key = link_type_choice[0]
        link_type_display = link_type_choice[1]
        profile_count = all_links.filter(link_type=link_type_key).values('profile').distinct().count()
        profiles_by_platform[link_type_display] = profile_count
    
    # Platform coverage (percentage of profiles using each platform)
    total_profiles = Profile.objects.count()
    platform_coverage = {}
    if total_profiles > 0:
        for platform, count in profiles_by_platform.items():
            coverage_percentage = round((count / total_profiles) * 100, 1)
            platform_coverage[platform] = coverage_percentage
    
    stats = {
        'total_links': total_links,
        'unique_link_types': unique_link_types,
        'profiles_with_links': profiles_with_links,
        'total_profiles': total_profiles,
        'link_type_distribution': link_type_distribution,
        'most_popular_platforms': most_popular_platforms,
        'profiles_by_platform': profiles_by_platform,
        'platform_coverage': platform_coverage,
        'available_link_types': [{'key': choice[0], 'display': choice[1]} for choice in SocialLink.LINK_TYPES],
    }
    
    return Response(stats)
