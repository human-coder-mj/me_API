from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from profile_api.models import Profile
from profile_api.views import IsAdminUserOrReadOnly
from .models import WorkExperience
from .serializers import WorkExperienceSerializer, WorkExperienceCreateSerializer


class WorkExperienceListCreateView(generics.ListCreateAPIView):
    """
    List all work experiences or create a new one
    GET: Public access
    POST: Admin only
    """
    queryset = WorkExperience.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkExperienceCreateSerializer
        return WorkExperienceSerializer
    
    def get_queryset(self):
        """
        Filter work experiences by query parameters
        """
        queryset = WorkExperience.objects.select_related('profile').all()
        
        # Filter by profile name
        profile_name = self.request.query_params.get('profile_name')
        if profile_name:
            queryset = queryset.filter(profile__name__icontains=profile_name)
        
        # Filter by company
        company = self.request.query_params.get('company')
        if company:
            queryset = queryset.filter(company__icontains=company)
        
        # Filter by position
        position = self.request.query_params.get('position')
        if position:
            queryset = queryset.filter(position__icontains=position)
        
        # Filter by current positions only
        current_only = self.request.query_params.get('current_only')
        if current_only and current_only.lower() == 'true':
            queryset = queryset.filter(is_current=True)
        
        # Search across multiple fields
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(company__icontains=search) |
                Q(position__icontains=search) |
                Q(location__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset


class WorkExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a work experience instance
    GET: Public access
    PUT/PATCH/DELETE: Admin only
    """
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer
    permission_classes = [IsAdminUserOrReadOnly]


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
        return Response(serializer.data)
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
