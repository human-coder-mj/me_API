from rest_framework import serializers
from .models import SocialLink
from profile_api.models import Profile


class SocialLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for SocialLink model
    """
    profile_name = serializers.CharField(source='profile.name', read_only=True)
    link_type_display = serializers.CharField(source='get_link_type_display', read_only=True)
    
    class Meta:
        model = SocialLink
        fields = [
            'id', 'profile', 'profile_name', 'link_type', 
            'link_type_display', 'url', 'display_name'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        """
        Custom validation for social links
        """
        # Check for duplicate link type for the same profile
        profile = data.get('profile')
        link_type = data.get('link_type')
        
        if profile and link_type:
            # If updating, exclude current instance
            queryset = SocialLink.objects.filter(profile=profile, link_type=link_type)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                link_type_display = dict(SocialLink.LINK_TYPES).get(link_type, link_type)
                raise serializers.ValidationError(
                    f"A {link_type_display} link already exists for this profile"
                )
        
        return data


class SocialLinkCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating SocialLink with profile name
    """
    profile_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = SocialLink
        fields = ['profile_name', 'link_type', 'url', 'display_name']

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
        Custom validation for social links
        """
        # Get profile and check for duplicate link type
        profile_name = data.get('profile_name')
        link_type = data.get('link_type')
        
        if profile_name and link_type:
            try:
                profile = Profile.objects.get(name__iexact=profile_name)
                if SocialLink.objects.filter(profile=profile, link_type=link_type).exists():
                    link_type_display = dict(SocialLink.LINK_TYPES).get(link_type, link_type)
                    raise serializers.ValidationError(
                        f"A {link_type_display} link already exists for profile '{profile_name}'"
                    )
            except Profile.DoesNotExist:
                pass  # Will be caught by profile_name validation
        
        return data

    def create(self, validated_data):
        """
        Create social link with profile lookup
        """
        profile_name = validated_data.pop('profile_name')
        profile = Profile.objects.get(name__iexact=profile_name)
        validated_data['profile'] = profile
        return super().create(validated_data)


class SocialLinkSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for social link summaries
    """
    profile_name = serializers.CharField(source='profile.name', read_only=True)
    link_type_display = serializers.CharField(source='get_link_type_display', read_only=True)
    
    class Meta:
        model = SocialLink
        fields = ['id', 'profile_name', 'link_type', 'link_type_display', 'url', 'display_name']


class SocialLinksByTypeSerializer(serializers.Serializer):
    """
    Serializer for social links grouped by type
    """
    link_type = serializers.CharField()
    link_type_display = serializers.CharField()
    links = SocialLinkSerializer(many=True)
    link_count = serializers.IntegerField()


class SocialStatsSerializer(serializers.Serializer):
    """
    Serializer for social link statistics
    """
    total_links = serializers.IntegerField()
    unique_link_types = serializers.IntegerField()
    profiles_with_links = serializers.IntegerField()
    link_type_distribution = serializers.DictField()
    most_popular_platforms = serializers.ListField()
    profiles_by_platform = serializers.DictField()
    available_link_types = serializers.ListField()
