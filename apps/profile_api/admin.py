from django.contrib import admin
from education_api.models import Education
from skills_api.models import Skill
from projects_api.models import Project
from experience_api.models import WorkExperience
from social_api.models import SocialLink
from .models import Profile


class EducationInline(admin.TabularInline):
    """Inline admin for Education"""
    
    model = Education
    extra = 1
    fields = ('institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'grade', 'description')


class SkillInline(admin.TabularInline):
    """Inline admin for Skills"""
    
    model = Skill
    extra = 1
    fields = ('name', 'level', 'category')


class ProjectInline(admin.StackedInline):
    """Inline admin for Projects"""
    
    model = Project
    extra = 1
    fields = (
        'title', 'description', 'technologies', 
        ('github_link', 'live_link', 'demo_link'),
        ('start_date', 'end_date', 'is_featured')
    )


class WorkExperienceInline(admin.StackedInline):
    """Inline admin for Work Experience"""
    
    model = WorkExperience
    extra = 1
    fields = (
        ('company', 'position'),
        ('location', 'is_current'),
        ('start_date', 'end_date'),
        'description', 'achievements'
    )


class SocialLinkInline(admin.TabularInline):
    """Inline admin for Social Links"""
    
    model = SocialLink
    extra = 1
    fields = ('link_type', 'url', 'display_name')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Comprehensive admin interface for Profile with all related data
    """
    list_display = ('name', 'email', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'email', 'bio')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'bio'),
            'description': 'Basic profile information'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Add all related data as inlines if apps are available

    inlines = [
        EducationInline,
        SkillInline, 
        ProjectInline,
        WorkExperienceInline,
        SocialLinkInline,
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch_related for better performance"""
        qs = super().get_queryset(request)
        
        qs = qs.prefetch_related(
            'education', 'skills', 'projects', 
            'work_experiences', 'social_links'
        )
        return qs
