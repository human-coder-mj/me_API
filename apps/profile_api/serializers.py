from rest_framework import serializers
from education_api.models import Education
from skills_api.models import Skill
from projects_api.models import Project
from experience_api.models import WorkExperience
from social_api.models import SocialLink
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Main serializer for Profile model - handles both read and write operations
    """

    class Meta:
        model = Profile
        fields = ['id', 'name', 'email', 'bio', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


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
            'id', 'name', 'email', 'bio',
            'education', 'skills', 'projects', 'work_experiences', 'social_links'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_education(self, obj):
        """Get education data from education_api"""
        try:
            
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
