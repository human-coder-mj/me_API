from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from profile_api.models import Profile
from me_API.permissions import IsAdminUserOrReadOnly
from .models import Education
from .serializers import EducationSerializer,\
    EducationListSerializer, EducationCreateUpdateSerializer



class EducationListCreateView(generics.ListCreateAPIView):
    """
    API view to retrieve list of education records (public) or create new education (admin only)
    """
    queryset = Education.objects.all().select_related('profile')
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EducationListSerializer
        return EducationCreateUpdateSerializer
    
    def get_queryset(self):
        """
        Filter education records based on query parameters
        """
        queryset = Education.objects.all().select_related('profile')
        
        # Filter by profile ID
        profile_id = self.request.query_params.get('profile', None)
        if profile_id:
            queryset = queryset.filter(profile_id=profile_id)

        # Filter by institution
        institution = self.request.query_params.get('institution', None)
        if institution:
            queryset = queryset.filter(institution__icontains=institution)

        # Filter by degree
        degree = self.request.query_params.get('degree', None)
        if degree:
            queryset = queryset.filter(degree__icontains=degree)

        # Filter by field of study
        field = self.request.query_params.get('field', None)
        if field:
            queryset = queryset.filter(field_of_study__icontains=field)

        return queryset.order_by('-start_date')


class EducationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve education (public) or update/delete (admin only)
    """
    queryset = Education.objects.all().select_related('profile')
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EducationCreateUpdateSerializer
        return EducationSerializer

@api_view(['GET'])
def education_by_profile_name(request, name):
    """
    API view to get all education records for a profile by name
    """
    try:
        # Get profile by name (case-insensitive)
        profile = Profile.objects.get(name__iexact=name)
        
        # Get education records for this profile
        education_records = Education.objects.filter(profile=profile).order_by('-start_date')
        serializer = EducationListSerializer(education_records, many=True)
        
        return Response({
            'profile_name': profile.name,
            'profile_id': profile.id,
            'education_count': len(education_records),
            'education': serializer.data
        })
        
    except Profile.DoesNotExist:
        return Response(
            {'error': f'Profile with name "{name}" does not exist'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception:
        return Response(
            {'error': 'Failed to fetch education records'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def education_search(request):
    """
    API view for searching education records
    GET /education/search?q=university
    """
    query = request.GET.get('q', '').strip()
    if not query:
        return Response(
            {'error': 'q parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Search across multiple fields
    education_records = Education.objects.filter(
        Q(institution__icontains=query) |
        Q(degree__icontains=query) |
        Q(field_of_study__icontains=query) |
        Q(description__icontains=query)
    ).select_related('profile').order_by('-start_date')
    
    results = []
    for education in education_records:
        education_data = {
            'id': education.id,
            'institution': education.institution,
            'degree': education.degree,
            'field_of_study': education.field_of_study,
            'start_date': education.start_date,
            'end_date': education.end_date,
            'profile': {
                'id': education.profile.id,
                'name': education.profile.name
            },
            'match_type': []
        }
        
        # Determine what matched
        if query.lower() in education.institution.lower():
            education_data['match_type'].append('institution')
        if query.lower() in education.degree.lower():
            education_data['match_type'].append('degree')
        if query.lower() in (education.field_of_study or '').lower():
            education_data['match_type'].append('field_of_study')
        if query.lower() in (education.description or '').lower():
            education_data['match_type'].append('description')
            
        results.append(education_data)
    
    return Response({
        'query': query,
        'results_count': len(results),
        'results': results
    })


class EducationStatsView(APIView):
    """
    API view to get education statistics
    """
    def get(self, request):
        total_education = Education.objects.count()
        total_institutions = Education.objects.values('institution').distinct().count()
        total_degrees = Education.objects.values('degree').distinct().count()
        ongoing_education = Education.objects.filter(end_date__isnull=True).count()
        
        return Response({
            'total_education_records': total_education,
            'total_institutions': total_institutions,
            'total_degrees': total_degrees,
            'ongoing_education': ongoing_education
        })
