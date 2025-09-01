from rest_framework import serializers
from .models import Profile


# Constants
EMAIL_EXISTS_ERROR = "A profile with this email already exists."


class ProfileSerializer(serializers.ModelSerializer):
    """
    Main serializer for Profile model - handles both read and write operations
    """

    class Meta:
        model = Profile
        fields = ['id', 'name', 'email', 'bio', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_email(self, value):
        """
        Validate email uniqueness for both create and update operations
        """
        # For updates, check if email is being changed and if new email exists
        if self.instance and self.instance.email != value:
            if Profile.objects.filter(email=value).exists():
                raise serializers.ValidationError(EMAIL_EXISTS_ERROR)

        # For creation, check if email already exists
        elif not self.instance and Profile.objects.filter(email=value).exists():
            raise serializers.ValidationError(EMAIL_EXISTS_ERROR)

        return value


class ProfileListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing profiles 
    """
    
    class Meta:
        model = Profile
        fields = ['id', 'name', 'email', 'bio']


class ComprehensiveProfileSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer that includes all related data from other apps
    """
    # Related data from other apps (will be populated by SerializerMethodField)
    education = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    work_experiences = serializers.SerializerMethodField()
    social_links = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'name', 'email', 'bio', 'created_at', 'updated_at',
            'education', 'skills', 'projects', 'work_experiences', 'social_links'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_education(self, obj):
        """Get education data from education_api"""
        try:
            from apps.education_api.models import Education
            education_list = Education.objects.filter(profile=obj)
            return [
                {
                    'id': edu.id,
                    'institution': edu.institution,
                    'degree': edu.degree,
                    'field_of_study': edu.field_of_study,
                    'start_date': edu.start_date,
                    'end_date': edu.end_date,
                    'grade': edu.grade,
                    'description': edu.description
                }
                for edu in education_list
            ]
        except ImportError:
            return []

    def get_skills(self, obj):
        """Get skills data from skills_api"""
        try:
            from apps.skills_api.models import Skill
            skills_list = Skill.objects.filter(profile=obj)
            return [
                {
                    'id': skill.id,
                    'name': skill.name,
                    'level': skill.level,
                    'category': skill.category
                }
                for skill in skills_list
            ]
        except ImportError:
            return []

    def get_projects(self, obj):
        """Get projects data from projects_api"""
        try:
            from apps.projects_api.models import Project
            projects_list = Project.objects.filter(profile=obj)
            return [
                {
                    'id': project.id,
                    'title': project.title,
                    'description': project.description,
                    'technologies': project.technologies,
                    'links': {
                        'github': project.github_link,
                        'live': project.live_link,
                        'demo': project.demo_link
                    },
                    'start_date': project.start_date,
                    'end_date': project.end_date,
                    'is_featured': project.is_featured
                }
                for project in projects_list
            ]
        except ImportError:
            return []

    def get_work_experiences(self, obj):
        """Get work experience data from experience_api"""
        try:
            from apps.experience_api.models import WorkExperience
            work_list = WorkExperience.objects.filter(profile=obj)
            return [
                {
                    'id': work.id,
                    'company': work.company,
                    'position': work.position,
                    'location': work.location,
                    'start_date': work.start_date,
                    'end_date': work.end_date,
                    'is_current': work.is_current,
                    'description': work.description,
                    'achievements': work.achievements
                }
                for work in work_list
            ]
        except ImportError:
            return []

    def get_social_links(self, obj):
        """Get social links data from social_api"""
        try:
            from apps.social_api.models import SocialLink
            links_list = SocialLink.objects.filter(profile=obj)
            links_dict = {}
            for link in links_list:
                links_dict[link.link_type] = {
                    'url': link.url,
                    'display_name': link.display_name
                }
            return links_dict
        except ImportError:
            return {}
