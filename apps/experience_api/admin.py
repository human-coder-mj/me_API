from django.contrib import admin
from .models import WorkExperience


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    """
    Admin configuration for WorkExperience model
    """
    list_display = [
        'position', 'company', 'profile', 'start_date', 
        'end_date', 'is_current', 'location'
    ]
    list_filter = [
        'is_current', 'company', 'position', 'start_date', 'end_date'
    ]
    search_fields = [
        'position', 'company', 'location', 'description', 
        'achievements', 'profile__name', 'profile__email'
    ]
    ordering = ['-start_date']
    readonly_fields = ['id']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('profile', 'company', 'position', 'location')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'is_current'),
            'description': 'Set is_current to True for ongoing positions'
        }),
        ('Details', {
            'fields': ('description', 'achievements'),
            'classes': ('wide',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related('profile')
    
    def save_model(self, request, obj, form, change):
        """
        Custom save logic
        """
        # If is_current is True, clear end_date
        if obj.is_current:
            obj.end_date = None
        super().save_model(request, obj, form, change)
    
    actions = ['mark_as_current', 'mark_as_past']
    
    def mark_as_current(self, request, queryset):
        """
        Mark selected experiences as current
        """
        updated = queryset.update(is_current=True, end_date=None)
        self.message_user(request, f'{updated} experiences marked as current.')
    mark_as_current.short_description = "Mark selected experiences as current"
    
    def mark_as_past(self, request, queryset):
        """
        Mark selected experiences as past (requires manual end_date setting)
        """
        updated = queryset.update(is_current=False)
        self.message_user(
            request, 
            f'{updated} experiences marked as past. '
            'Please set end_date for each manually.'
        )
    mark_as_past.short_description = "Mark selected experiences as past"
