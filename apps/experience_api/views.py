from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count
from profile_api.models import Profile
from profile_api.views import IsAdminUserOrReadOnly
from .models import WorkExperience
from .serializers import WorkExperienceSerializer


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def experience_by_profile_name(request, name):
    """
    Get all work experiences for a specific profile by name
    """
    try:
        profile = Profile.objects.get(name__iexact=name)
        experiences = WorkExperience.objects.filter(profile=profile).order_by('-start_date')
        serializer = WorkExperienceSerializer(experiences, many=True)
        
        return Response({
            'profile_name': profile.name,
            'profile_id': profile.id,
            'experience_count': experiences.count(),
            'experiences': serializer.data
        })
    except Profile.DoesNotExist:
        return Response(
            {'error': f'Profile with name "{name}" not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def experience_stats(request):
    """
    Get work experience statistics
    """
    stats = {
        'total_experiences': WorkExperience.objects.count(),
        'current_positions': WorkExperience.objects.filter(is_current=True).count(),
        'past_positions': WorkExperience.objects.filter(is_current=False).count(),
        'unique_companies': WorkExperience.objects.values('company').distinct().count(),
        'unique_positions': WorkExperience.objects.values('position').distinct().count(),
    }
    
    # Most common companies
    companies = WorkExperience.objects.values('company').annotate(
        count=Count('company')
    ).order_by('-count')[:5]
    stats['top_companies'] = list(companies)
    
    # Most common positions
    positions = WorkExperience.objects.values('position').annotate(
        count=Count('position')
    ).order_by('-count')[:5]
    stats['top_positions'] = list(positions)
    
    return Response(stats)
