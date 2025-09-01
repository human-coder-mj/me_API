from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from profile_api.models import Profile
from profile_api.views import IsAdminUserOrReadOnly
from .models import Project
from .serializers import (
    ProjectSerializer, 
    ProjectCreateSerializer, 
    ProjectSummarySerializer
)


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    List all projects or create a new one
    GET: Public access
    POST: Admin only
    """
    queryset = Project.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectSerializer
    
    def get_queryset(self):
        """
        Filter projects by query parameters
        """
        queryset = Project.objects.select_related('profile').all()
        
        # Filter by profile name
        profile_name = self.request.query_params.get('profile_name')
        if profile_name:
            queryset = queryset.filter(profile__name__icontains=profile_name)
        
        # Filter by technology
        technology = self.request.query_params.get('technology')
        if technology:
            queryset = queryset.filter(technologies__icontains=technology)
        
        # Filter by featured projects only
        featured_only = self.request.query_params.get('featured_only')
        if featured_only and featured_only.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Filter by projects with live links
        has_live_link = self.request.query_params.get('has_live_link')
        if has_live_link and has_live_link.lower() == 'true':
            queryset = queryset.filter(live_link__isnull=False).exclude(live_link='')
        
        # Filter by projects with GitHub links
        has_github = self.request.query_params.get('has_github')
        if has_github and has_github.lower() == 'true':
            queryset = queryset.filter(github_link__isnull=False).exclude(github_link='')
        
        # Search across multiple fields
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(technologies__icontains=search)
            )
        
        # Get summary view
        summary = self.request.query_params.get('summary')
        if summary and summary.lower() == 'true':
            self.serializer_class = ProjectSummarySerializer
        
        return queryset


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a project instance
    GET: Public access
    PUT/PATCH/DELETE: Admin only
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminUserOrReadOnly]


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def projects_by_profile_name(request, name):
    """
    Get all projects for a specific profile by name
    """
    try:
        profile = Profile.objects.get(name__iexact=name)
        projects = Project.objects.filter(profile=profile).order_by('-is_featured', '-start_date')
        
        # Check if summary view is requested
        summary = request.query_params.get('summary')
        if summary and summary.lower() == 'true':
            serializer = ProjectSummarySerializer(projects, many=True)
        else:
            serializer = ProjectSerializer(projects, many=True)
            
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response(
            {'error': f'Profile with name "{name}" not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def featured_projects(request):
    """
    Get all featured projects across all profiles
    """
    projects = Project.objects.filter(is_featured=True).select_related('profile').order_by('-start_date')
    
    # Check if summary view is requested
    summary = request.query_params.get('summary')
    if summary and summary.lower() == 'true':
        serializer = ProjectSummarySerializer(projects, many=True)
    else:
        serializer = ProjectSerializer(projects, many=True)
        
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def projects_by_technology(request, technology):
    """
    Get all projects that use a specific technology
    """
    projects = Project.objects.filter(
        technologies__icontains=technology
    ).select_related('profile').order_by('-is_featured', '-start_date')
    
    # Check if summary view is requested
    summary = request.query_params.get('summary')
    if summary and summary.lower() == 'true':
        serializer = ProjectSummarySerializer(projects, many=True)
    else:
        serializer = ProjectSerializer(projects, many=True)
        
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def project_stats(request):
    """
    Get project statistics
    """
    stats = {
        'total_projects': Project.objects.count(),
        'featured_projects': Project.objects.filter(is_featured=True).count(),
        'projects_with_live_links': Project.objects.filter(
            live_link__isnull=False
        ).exclude(live_link='').count(),
        'projects_with_github': Project.objects.filter(
            github_link__isnull=False
        ).exclude(github_link='').count(),
        'projects_with_demo': Project.objects.filter(
            demo_link__isnull=False
        ).exclude(demo_link='').count(),
    }
    
    # Most used technologies
    all_projects = Project.objects.exclude(technologies='').exclude(technologies__isnull=True)
    technology_count = {}
    
    for project in all_projects:
        techs = [tech.strip() for tech in project.technologies.split(',') if tech.strip()]
        for tech in techs:
            technology_count[tech] = technology_count.get(tech, 0) + 1
    
    # Sort technologies by usage count
    sorted_techs = sorted(technology_count.items(), key=lambda x: x[1], reverse=True)
    stats['top_technologies'] = [
        {'technology': tech, 'count': count} 
        for tech, count in sorted_techs[:10]
    ]
    
    # Projects per profile
    profile_stats = Project.objects.values('profile__name').annotate(
        project_count=Count('id'),
        featured_count=Count('id', filter=Q(is_featured=True))
    ).order_by('-project_count')[:5]
    stats['top_profiles'] = list(profile_stats)
    
    return Response(stats)
