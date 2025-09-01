from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.db.models import Q, Count
from experience_api.models import WorkExperience
from social_api.models import SocialLink
from projects_api.models import Project
from skills_api.models import Skill
from .models import Profile
from .serializers import ProfileSerializer, ProfileListSerializer, ComprehensiveProfileSerializer


class IsAdminUserOrReadOnly(IsAdminUser):
    """
    Custom permission class: Only admin users can create/update/delete.
    Anyone can read (GET requests are allowed for everyone).
    """
    def has_permission(self, request, view):
        # Allow read permissions for any request (GET, HEAD, OPTIONS)
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # For write permissions, only allow admin users
        return super().has_permission(request, view)


class ProfileListCreateView(generics.ListCreateAPIView):
    """
    API view to retrieve list of profiles (public) or create a new profile (admin only)
    """
    queryset = Profile.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProfileListSerializer
        return ProfileSerializer


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve profile (public) or update/delete (admin only)
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class ComprehensiveProfileView(generics.RetrieveAPIView):
    """
    API view to retrieve comprehensive profile with all related data (public access)
    """
    queryset = Profile.objects.all()
    serializer_class = ComprehensiveProfileSerializer
    # No permission classes needed - public read-only access


@api_view(['GET'])
def profile_by_name(request, name):
    """
    API view to retrieve a profile by name
    """
    try:
        # Use iexact for case-insensitive exact match
        profile = Profile.objects.get(name__iexact=name)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response(
            {'error': f'Profile with name "{name}" does not exist'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def comprehensive_profile_by_name(request, name):
    """
    API view to retrieve comprehensive profile by name
    """
    try:
        # Use iexact for case-insensitive exact match
        profile = Profile.objects.get(name__iexact=name)
        serializer = ComprehensiveProfileSerializer(profile)
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response(
            {'error': f'Profile with name "{name}" does not exist'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def projects_by_skill(request):
    """
    API view to get projects filtered by skill
    GET /projects?skill=python
    """
    skill_name = request.GET.get('skill', '').lower()
    if not skill_name:
        return Response(
            {'error': 'skill parameter is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        
        # Find profiles that have the specified skill
        profiles_with_skill = Skill.objects.filter(
            name__icontains=skill_name
        ).values_list('profile_id', flat=True)
        
        # Get projects from those profiles
        projects = Project.objects.filter(profile_id__in=profiles_with_skill)
        
        projects_data = [
            {
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'technologies': project.technologies,
                'github_link': project.github_link,
                'live_link': project.live_link,
                'demo_link': project.demo_link,
                'is_featured': project.is_featured,
                'profile': {
                    'id': project.profile.id,
                    'name': project.profile.name,
                    'email': project.profile.email
                }
            }
            for project in projects
        ]
        
        return Response({
            'skill': skill_name,
            'projects_count': len(projects_data),
            'projects': projects_data
        })
        
    except ImportError:
        return Response(
            {'error': 'Required apps not available'}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['GET'])
def top_skills(request):
    """
    API view to get top skills by usage
    GET /skills/top
    """
    try:
        # Get skills with count of how many profiles have them
        top_skills = Skill.objects.values('name', 'category').annotate(
            usage_count=Count('profile')
        ).order_by('-usage_count')[:10]
        
        return Response({
            'top_skills': list(top_skills)
        })
        
    except ImportError:
        return Response(
            {'error': 'Skills app not available'}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['GET'])
def search_profiles(request):
    """
    API view for general search across profiles
    GET /search?q=developer
    """
    query = request.GET.get('q', '').strip()
    if not query:
        return Response(
            {'error': 'q parameter is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Search in profile fields
    profiles = Profile.objects.filter(
        Q(name__icontains=query) |
        Q(email__icontains=query) |
        Q(bio__icontains=query)
    )
    
    results = []
    for profile in profiles:
        # Try to add related data for more comprehensive search results
        profile_data = {
            'id': profile.id,
            'name': profile.name,
            'email': profile.email,
            'bio': profile.bio,
            'match_type': []
        }
        
        # Determine what matched
        if query.lower() in profile.name.lower():
            profile_data['match_type'].append('name')
        if query.lower() in profile.email.lower():
            profile_data['match_type'].append('email')
        if query.lower() in profile.bio.lower():
            profile_data['match_type'].append('bio')
            
        results.append(profile_data)
    
    return Response({
        'query': query,
        'results_count': len(results),
        'results': results
    })


class ProfileStatsView(APIView):
    """
    API view to get profile statistics
    """
    def get(self, request):
        total_profiles = Profile.objects.count()

        stats = {'total_profiles': total_profiles}

        # Try to get stats from other apps
        try:
            stats['total_skills'] = Skill.objects.count()
            stats['unique_skills'] = Skill.objects.values('name').distinct().count()
        except ImportError:
            pass

        try:
            stats['total_projects'] = Project.objects.count()
            stats['featured_projects'] = Project.objects.filter(is_featured=True).count()
        except ImportError:
            pass

        try:
            stats['total_work_experiences'] = WorkExperience.objects.count()
        except ImportError:
            pass

        try:
            stats['total_social_links'] = SocialLink.objects.count()
        except ImportError:
            pass

        return Response(stats)


@api_view(['GET'])
def api_documentation(request):
    """
    API documentation endpoint explaining the public portfolio API
    """
    documentation = {
        "title": "Personal Portfolio API",
        "description": "Public API for viewing professional portfolio details. Read access is public, write access requires admin privileges.",
        "version": "1.0",
        "access_policy": {
            "read_access": "Public - Anyone can view portfolio data",
            "write_access": "Admin only - Only admin users can create/update/delete data"
        },
        "endpoints": {
            "profiles": {
                "GET /api/v1/profiles/": "List all profiles (public)",
                "POST /api/v1/profiles/": "Create new profile (admin only)",
                "GET /api/v1/profiles/{id}/": "Get specific profile (public)",
                "PUT /api/v1/profiles/{id}/": "Update profile (admin only)",
                "DELETE /api/v1/profiles/{id}/": "Delete profile (admin only)",
                "GET /api/v1/profiles/{id}/comprehensive/": "Get profile with all related data (public)",
                "GET /api/v1/profile/{name}/": "Get comprehensive profile by name (public) - Main endpoint",
                "GET /api/v1/profiles/name/{name}/": "Get basic profile by name (public)"
            },
            "query_endpoints": {
                "GET /api/v1/projects?skill=python": "Filter projects by skill (public)",
                "GET /api/v1/skills/top": "Get top skills by usage (public)",
                "GET /api/v1/search?q=keyword": "Search across profiles (public)"
            },
            "statistics": {
                "GET /api/v1/stats/": "Get API statistics (public)"
            },
            "admin_features": {
                "description": "Admin users can create complete profiles with all related data",
                "admin_panel": "/admin/ - Full Django admin interface",
                "features": [
                    "Create profile with education, skills, projects, work experience, social links",
                    "Inline editing of all related data",
                    "Bulk operations and advanced filtering",
                    "Individual model management for each category"
                ]
            }
        },
        "example_responses": {
            "comprehensive_profile": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "bio": "Software Developer",
                "education": [
                    {
                        "institution": "University XYZ",
                        "degree": "Bachelor of Computer Science",
                        "field_of_study": "Computer Science",
                        "start_date": "2018-09-01",
                        "end_date": "2022-06-01"
                    }
                ],
                "skills": [
                    {
                        "name": "Python",
                        "level": "advanced",
                        "category": "Programming"
                    }
                ],
                "projects": [
                    {
                        "title": "Portfolio Website",
                        "description": "Personal portfolio built with Django",
                        "technologies": "Python, Django, PostgreSQL",
                        "links": {
                            "github": "https://github.com/user/portfolio",
                            "live": "https://example.com",
                            "demo": None
                        }
                    }
                ],
                "work_experiences": [
                    {
                        "company": "Tech Corp",
                        "position": "Software Developer",
                        "is_current": True,
                        "description": "Developing web applications"
                    }
                ],
                "social_links": {
                    "github": {
                        "url": "https://github.com/johndoe",
                        "display_name": "johndoe"
                    },
                    "linkedin": {
                        "url": "https://linkedin.com/in/johndoe",
                        "display_name": "John Doe"
                    }
                }
            }
        }
    }
    
    return Response(documentation)
