from rest_framework import serializers
from .models import Skill
from profile_api.models import Profile


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for Skill model
    """
    profile_name = serializers.CharField(source='profile.name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = Skill
        fields = [
            'id', 'profile', 'profile_name', 'name', 'level', 
            'level_display', 'category'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        """
        Custom validation for skills
        """
        # Check for duplicate skill name for the same profile
        profile = data.get('profile')
        name = data.get('name')
        
        if profile and name:
            # If updating, exclude current instance
            queryset = Skill.objects.filter(profile=profile, name__iexact=name)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    f"Skill '{name}' already exists for this profile"
                )
        
        return data


class SkillCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Skill with profile name
    """
    profile_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = Skill
        fields = ['profile_name', 'name', 'level', 'category']

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
        Custom validation for skills
        """
        # Get profile and check for duplicate skill name
        profile_name = data.get('profile_name')
        name = data.get('name')
        
        if profile_name and name:
            try:
                profile = Profile.objects.get(name__iexact=profile_name)
                if Skill.objects.filter(profile=profile, name__iexact=name).exists():
                    raise serializers.ValidationError(
                        f"Skill '{name}' already exists for profile '{profile_name}'"
                    )
            except Profile.DoesNotExist:
                pass  # Will be caught by profile_name validation
        
        return data

    def create(self, validated_data):
        """
        Create skill with profile lookup
        """
        profile_name = validated_data.pop('profile_name')
        profile = Profile.objects.get(name__iexact=profile_name)
        validated_data['profile'] = profile
        return super().create(validated_data)


class SkillSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for skill summaries
    """
    profile_name = serializers.CharField(source='profile.name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = Skill
        fields = ['id', 'profile_name', 'name', 'level', 'level_display', 'category']


class SkillsByCategorySerializer(serializers.Serializer):
    """
    Serializer for skills grouped by category
    """
    category = serializers.CharField()
    skills = SkillSerializer(many=True)
    skill_count = serializers.IntegerField()
    level_breakdown = serializers.DictField()


class SkillStatsSerializer(serializers.Serializer):
    """
    Serializer for skill statistics
    """
    total_skills = serializers.IntegerField()
    unique_skills = serializers.IntegerField()
    categories_count = serializers.IntegerField()
    level_distribution = serializers.DictField()
    top_categories = serializers.ListField()
    top_skills = serializers.ListField()
    profiles_with_skills = serializers.IntegerField()
