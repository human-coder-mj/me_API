from rest_framework import serializers
from .models import WorkExperience
from profile_api.models import Profile


class WorkExperienceSerializer(serializers.ModelSerializer):
    """
    Serializer for WorkExperience model
    """
    profile_name = serializers.CharField(source='profile.name', read_only=True)
    
    class Meta:
        model = WorkExperience
        fields = [
            'id', 'profile', 'profile_name', 'company', 'position', 
            'location', 'start_date', 'end_date', 'is_current', 
            'description', 'achievements'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        """
        Custom validation for work experience
        """
        # If end_date is provided and is_current is True, raise error
        if data.get('is_current') and data.get('end_date'):
            raise serializers.ValidationError(
                "Cannot have end_date if position is current"
            )
        
        # If not current and no end_date, raise error
        if not data.get('is_current') and not data.get('end_date'):
            raise serializers.ValidationError(
                "End date is required for non-current positions"
            )
        
        # If both start_date and end_date exist, validate order
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "Start date must be before end date"
            )
        
        return data


class WorkExperienceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating WorkExperience with profile name
    """
    profile_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = WorkExperience
        fields = [
            'profile_name', 'company', 'position', 'location', 
            'start_date', 'end_date', 'is_current', 
            'description', 'achievements'
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
        Custom validation for work experience
        """
        # If end_date is provided and is_current is True, raise error
        if data.get('is_current') and data.get('end_date'):
            raise serializers.ValidationError(
                "Cannot have end_date if position is current"
            )
        
        # If not current and no end_date, raise error
        if not data.get('is_current') and not data.get('end_date'):
            raise serializers.ValidationError(
                "End date is required for non-current positions"
            )
        
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
        Create work experience with profile lookup
        """
        profile_name = validated_data.pop('profile_name')
        profile = Profile.objects.get(name__iexact=profile_name)
        validated_data['profile'] = profile
        return super().create(validated_data)
