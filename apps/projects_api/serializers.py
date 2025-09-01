from rest_framework import serializers
from .models import Project
from profile_api.models import Profile


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model
    """
    profile_name = serializers.CharField(source='profile.name', read_only=True)
    technologies_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'profile', 'profile_name', 'title', 'description', 
            'technologies', 'technologies_list', 'github_link', 
            'live_link', 'demo_link', 'start_date', 'end_date', 'is_featured'
        ]
        read_only_fields = ['id']

    def get_technologies_list(self, obj):
        """
        Convert comma-separated technologies into a list
        """
        if obj.technologies:
            return [tech.strip() for tech in obj.technologies.split(',') if tech.strip()]
        return []

    def validate(self, data):
        """
        Custom validation for projects
        """
        # If both start_date and end_date exist, validate order
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "Start date must be before end date"
            )
        
        return data


class ProjectCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Project with profile name
    """
    profile_name = serializers.CharField(write_only=True)
    technologies_list = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False,
        help_text="List of technologies used in the project"
    )
    
    class Meta:
        model = Project
        fields = [
            'profile_name', 'title', 'description', 'technologies', 
            'technologies_list', 'github_link', 'live_link', 'demo_link', 
            'start_date', 'end_date', 'is_featured'
        ]

    def validate_profile_name(self, value):
        """
        Validate that profile exists
        """
        try:
            Profile.objects.get(name__iexact=value)
        except Profile.DoesNotExist:
            raise serializers.ValidationError(f"Profile with name '{value}' does not exist")
        return value

    def validate(self, data):
        """
        Custom validation for projects
        """
        # Convert technologies_list to comma-separated string if provided
        if 'technologies_list' in data and data['technologies_list']:
            if not data.get('technologies'):
                data['technologies'] = ', '.join(data['technologies_list'])
        
        # If both start_date and end_date exist, validate order
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "Start date must be before end date"
            )
        
        return data

    def create(self, validated_data):
        """
        Create project with profile lookup
        """
        profile_name = validated_data.pop('profile_name')
        validated_data.pop('technologies_list', None)  # Remove as it's already processed
        profile = Profile.objects.get(name__iexact=profile_name)
        validated_data['profile'] = profile
        return super().create(validated_data)


class ProjectSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for project summaries
    """
    profile_name = serializers.CharField(source='profile.name', read_only=True)
    technology_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'profile_name', 'title', 'is_featured', 
            'start_date', 'end_date', 'technology_count',
            'github_link', 'live_link', 'demo_link'
        ]

    def get_technology_count(self, obj):
        """
        Count number of technologies used
        """
        if obj.technologies:
            return len([tech.strip() for tech in obj.technologies.split(',') if tech.strip()])
        return 0
