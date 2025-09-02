from collections import defaultdict
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from profile_api.models import Profile
from profile_api.views import IsAdminUserOrReadOnly
from .models import Skill
from .serializers import (
    SkillSerializer,
    SkillCreateSerializer,
    SkillSummarySerializer,
)


class SkillListCreateView(generics.ListCreateAPIView):
    """
    List all skills or create a new one
    GET: Public access
    POST: Admin only
    """
    queryset = Skill.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SkillCreateSerializer
        return SkillSerializer
    
    def get_queryset(self):
        """
        Filter skills by query parameters
        """
        queryset = Skill.objects.select_related('profile').all()
        
        # Filter by profile name
        profile_name = self.request.query_params.get('profile_name')
        if profile_name:
            queryset = queryset.filter(profile__name__icontains=profile_name)
        
        # Filter by skill level
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        # Filter by skill name
        skill_name = self.request.query_params.get('skill_name')
        if skill_name:
            queryset = queryset.filter(name__icontains=skill_name)
        
        # Search across multiple fields
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(category__icontains=search) |
                Q(profile__name__icontains=search)
            )
        
        # Get summary view
        summary = self.request.query_params.get('summary')
        if summary and summary.lower() == 'true':
            self.serializer_class = SkillSummarySerializer
        
        return queryset


class SkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a skill instance
    GET: Public access
    PUT/PATCH/DELETE: Admin only
    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAdminUserOrReadOnly]


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def skills_by_profile_name(request, name):
    """
    Get all skills for a specific profile by name
    """
    try:
        profile = Profile.objects.get(name__iexact=name)
        skills = Skill.objects.filter(profile=profile).order_by('category', 'name')
        
        # Check if summary view is requested
        summary = request.query_params.get('summary')
        if summary and summary.lower() == 'true':
            serializer = SkillSummarySerializer(skills, many=True)
        else:
            serializer = SkillSerializer(skills, many=True)
            
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response(
            {'error': f'Profile with name "{name}" not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def skills_by_category(request, category):
    """
    Get all skills in a specific category
    """
    skills = Skill.objects.filter(
        category__icontains=category
    ).select_related('profile').order_by('level', 'name')
    
    # Check if summary view is requested
    summary = request.query_params.get('summary')
    if summary and summary.lower() == 'true':
        serializer = SkillSummarySerializer(skills, many=True)
    else:
        serializer = SkillSerializer(skills, many=True)
        
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def skills_by_level(request, level):
    """
    Get all skills at a specific level
    """
    skills = Skill.objects.filter(
        level=level
    ).select_related('profile').order_by('category', 'name')
    
    # Check if summary view is requested
    summary = request.query_params.get('summary')
    if summary and summary.lower() == 'true':
        serializer = SkillSummarySerializer(skills, many=True)
    else:
        serializer = SkillSerializer(skills, many=True)
        
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def skills_grouped_by_category(request):
    """
    Get skills grouped by category with statistics
    """
    skills = Skill.objects.select_related('profile').order_by('category', 'name')
    
    # Group skills by category
    categories = defaultdict(list)
    for skill in skills:
        category = skill.category or 'Uncategorized'
        categories[category].append(skill)
    
    # Build response data
    grouped_data = []
    for category, skill_list in categories.items():
        # Count skills by level in this category
        level_breakdown = defaultdict(int)
        for skill in skill_list:
            level_breakdown[skill.level] += 1
        
        grouped_data.append({
            'category': category,
            'skills': SkillSerializer(skill_list, many=True).data,
            'skill_count': len(skill_list),
            'level_breakdown': dict(level_breakdown)
        })
    
    # Sort by skill count descending
    grouped_data.sort(key=lambda x: x['skill_count'], reverse=True)
    
    return Response(grouped_data)


@api_view(['GET'])
@permission_classes([IsAdminUserOrReadOnly])
def skill_stats(request):
    """
    Get comprehensive skill statistics
    """
    all_skills = Skill.objects.select_related('profile')
    
    # Basic counts
    total_skills = all_skills.count()
    unique_skills = all_skills.values('name').distinct().count()
    categories = all_skills.exclude(category='').exclude(category__isnull=True).values('category').distinct()
    categories_count = categories.count()
    profiles_with_skills = all_skills.values('profile').distinct().count()
    
    # Level distribution
    level_distribution = {}
    for level_choice in Skill.SKILL_LEVELS:
        level_key = level_choice[0]
        level_count = all_skills.filter(level=level_key).count()
        level_distribution[level_choice[1]] = level_count
    
    # Top categories by skill count
    category_stats = all_skills.exclude(category='').exclude(category__isnull=True).values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    top_categories = [
        {'category': stat['category'], 'count': stat['count']} 
        for stat in category_stats
    ]
    
    # Most common skills across all profiles
    skill_stats = all_skills.values('name').annotate(
        count=Count('id'),
        profiles_count=Count('profile', distinct=True)
    ).order_by('-count')[:10]
    top_skills = [
        {
            'skill': stat['name'], 
            'total_count': stat['count'],
            'profiles_count': stat['profiles_count']
        } 
        for stat in skill_stats
    ]
    
    # Skills by level and category matrix
    level_category_matrix = {}
    for level_choice in Skill.SKILL_LEVELS:
        level_key = level_choice[0]
        level_name = level_choice[1]
        level_category_matrix[level_name] = {}
        
        for category_stat in category_stats[:5]:  # Top 5 categories
            category = category_stat['category']
            count = all_skills.filter(level=level_key, category=category).count()
            level_category_matrix[level_name][category] = count
    
    stats = {
        'total_skills': total_skills,
        'unique_skills': unique_skills,
        'categories_count': categories_count,
        'profiles_with_skills': profiles_with_skills,
        'level_distribution': level_distribution,
        'top_categories': top_categories,
        'top_skills': top_skills,
        'level_category_matrix': level_category_matrix,
        'available_levels': [choice[1] for choice in Skill.SKILL_LEVELS],
    }
    
    return Response(stats)

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