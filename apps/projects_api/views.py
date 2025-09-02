from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from profile_api.models import Profile
from skills_api.models import Skill
from me_API.permissions import IsAdminUserOrReadOnly
from .models import Project
from .serializers import (
    ProjectSerializer, 
    ProjectSummarySerializer
)


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



@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def projects_by_skill(request):
    """
    Enhanced API view to get projects filtered by skill with advanced filtering options
    GET /projects?skill=python&level=advanced&featured_only=true&summary=true
    """
    skill_name = request.GET.get('skill', '').strip()
    if not skill_name:
        return Response(
            {'error': 'skill parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Build skill filter query
        skill_filter = Q(name__icontains=skill_name)
        
        # Optional: Filter by skill level
        skill_level = request.GET.get('level', '').strip()
        if skill_level:
            skill_filter &= Q(level__iexact=skill_level)
        
        # Optional: Filter by skill category
        skill_category = request.GET.get('category', '').strip()
        if skill_category:
            skill_filter &= Q(category__icontains=skill_category)

        # Find profiles that have the specified skill
        profiles_with_skill = Skill.objects.filter(skill_filter).values_list('profile_id', flat=True)

        if not profiles_with_skill:
            return Response({
                'skill': skill_name,
                'level': skill_level or 'any',
                'category': skill_category or 'any',
                'projects_count': 0,
                'projects': [],
                'message': 'No profiles found with the specified skill criteria'
            })

        # Get projects from those profiles
        projects_query = Project.objects.filter(
            profile_id__in=profiles_with_skill
        ).select_related('profile').order_by('-is_featured', '-start_date')
        
        # Optional: Filter only featured projects
        featured_only = request.GET.get('featured_only', '').strip().lower()
        if featured_only == 'true':
            projects_query = projects_query.filter(is_featured=True)
        
        # Optional: Filter projects with live links
        has_live_link = request.GET.get('has_live_link', '').strip().lower()
        if has_live_link == 'true':
            projects_query = projects_query.filter(
                live_link__isnull=False
            ).exclude(live_link='')
        
        # Optional: Filter projects with GitHub links
        has_github = request.GET.get('has_github', '').strip().lower()
        if has_github == 'true':
            projects_query = projects_query.filter(
                github_link__isnull=False
            ).exclude(github_link='')

        projects = projects_query.all()
        
        # Check if summary view is requested
        summary = request.GET.get('summary', '').strip().lower()
        if summary == 'true':
            serializer = ProjectSummarySerializer(projects, many=True)
        else:
            serializer = ProjectSerializer(projects, many=True)

        # Get skill statistics for the response
        matching_skills = Skill.objects.filter(skill_filter).select_related('profile')
        skill_levels = matching_skills.values_list('level', flat=True)
        level_distribution = {}
        for level in skill_levels:
            level_distribution[level] = level_distribution.get(level, 0) + 1

        return Response({
            'skill': skill_name,
            'level_filter': skill_level or 'any',
            'category_filter': skill_category or 'any',
            'featured_only': featured_only == 'true',
            'has_live_link': has_live_link == 'true',
            'has_github': has_github == 'true',
            'projects_count': len(projects),
            'profiles_with_skill': len(profiles_with_skill),
            'skill_level_distribution': level_distribution,
            'projects': serializer.data
        })
        
    except ImportError:
        return Response(
            {'error': 'Required apps not available'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )