from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin configuration for Project model
    """
    list_display = [
        'title', 'profile', 'is_featured', 'start_date', 
        'end_date', 'has_github', 'has_live_link', 'technology_count'
    ]
    list_filter = [
        'is_featured', 'start_date', 'end_date', 'profile'
    ]
    search_fields = [
        'title', 'description', 'technologies', 
        'profile__name', 'profile__email'
    ]
    ordering = ['-is_featured', '-start_date']
    readonly_fields = ['id']
    date_hierarchy = 'start_date'
    list_editable = ['is_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('profile', 'title', 'description', 'is_featured')
        }),
        ('Technologies & Links', {
            'fields': ('technologies', 'github_link', 'live_link', 'demo_link'),
            'description': 'Enter technologies as comma-separated values'
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related('profile')
    
    def has_github(self, obj):
        """
        Check if project has GitHub link
        """
        return bool(obj.github_link)
    has_github.boolean = True
    has_github.short_description = 'GitHub'
    
    def has_live_link(self, obj):
        """
        Check if project has live link
        """
        return bool(obj.live_link)
    has_live_link.boolean = True
    has_live_link.short_description = 'Live Link'
    
    def technology_count(self, obj):
        """
        Count number of technologies
        """
        if obj.technologies:
            return len([tech.strip() for tech in obj.technologies.split(',') if tech.strip()])
        return 0
    technology_count.short_description = 'Tech Count'
    
    actions = ['mark_as_featured', 'mark_as_not_featured', 'clear_end_dates']
    
    def mark_as_featured(self, request, queryset):
        """
        Mark selected projects as featured
        """
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} projects marked as featured.')
    mark_as_featured.short_description = "Mark selected projects as featured"
    
    def mark_as_not_featured(self, request, queryset):
        """
        Mark selected projects as not featured
        """
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} projects marked as not featured.')
    mark_as_not_featured.short_description = "Mark selected projects as not featured"
    
    def clear_end_dates(self, request, queryset):
        """
        Clear end dates for ongoing projects
        """
        updated = queryset.update(end_date=None)
        self.message_user(request, f'End dates cleared for {updated} projects.')
    clear_end_dates.short_description = "Clear end dates (mark as ongoing)"
