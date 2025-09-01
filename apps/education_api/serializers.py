from rest_framework import serializers
from .models import Education


class EducationSerializer(serializers.ModelSerializer):
    """
    Main serializer for Education model - handles both read and write operations
    """
    
    class Meta:
        model = Education
        fields = [
            'id', 'profile', 'institution', 'degree', 'field_of_study',
            'start_date', 'end_date', 'grade', 'description'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """
        Validate that start_date is before end_date if end_date is provided
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "Start date must be before end date."
            )
        
        return data


class EducationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing education records
    """
    profile_name = serializers.CharField(source='profile.name', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Education
        fields = [
            'id', 'institution', 'degree', 'field_of_study',
            'start_date', 'end_date', 'profile_name', 'duration'
        ]
    
    def get_duration(self, obj):
        """Calculate duration of education"""
        if obj.end_date:
            duration = obj.end_date - obj.start_date
            years = duration.days // 365
            months = (duration.days % 365) // 30
            return f"{years} years, {months} months"
        else:
            return "Ongoing"


class EducationCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating education records (admin only)
    """
    
    class Meta:
        model = Education
        fields = [
            'profile', 'institution', 'degree', 'field_of_study',
            'start_date', 'end_date', 'grade', 'description'
        ]
    
    def validate(self, data):
        """
        Validate education data
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Validate date logic
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "Start date must be before end date."
            )
        
        # Validate required fields
        if not data.get('institution'):
            raise serializers.ValidationError(
                "Institution is required."
            )
        
        if not data.get('degree'):
            raise serializers.ValidationError(
                "Degree is required."
            )
        
        return data
