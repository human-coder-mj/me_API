from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.validators import ValidationError
from experience_api.models import WorkExperience
from social_api.models import SocialLink
from projects_api.models import Project
from skills_api.models import Skill
from me_API.permissions import IsAdminUserOrReadOnly
from .models import Profile
from .serializers import ProfileSerializer, ProfileListSerializer, ComprehensiveProfileSerializer
# Constants
EMAIL_EXISTS_ERROR = "A profile with this email already exists."



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

    def perform_create(self, serializer):
        """
        Handle profile creation with email validation
        """
        email = serializer.validated_data.get('email')
        if email and Profile.objects.filter(email=email).exists():
            raise ValidationError({'email': [EMAIL_EXISTS_ERROR]})
        serializer.save()


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve profile (public) or update/delete (admin only)
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def perform_update(self, serializer):
        """
        Handle profile update with email validation
        """
        email = serializer.validated_data.get('email')
        instance = serializer.instance
        
        # Check if email is being changed and if new email already exists
        if email and instance.email != email:
            if Profile.objects.filter(email=email).exists():
                raise ValidationError({'email': [EMAIL_EXISTS_ERROR]})
        serializer.save()


class ComprehensiveProfileView(generics.RetrieveAPIView):
    """
    API view to retrieve comprehensive profile with all related data (public access)
    """
    queryset = Profile.objects.all()
    serializer_class = ComprehensiveProfileSerializer
    # No permission classes needed - public read-only access


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
