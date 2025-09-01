from django.contrib import admin
from .models import Education


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """
    Admin interface for Education model
    """
    list_display = ('profile', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current')
    list_filter = ('degree', 'start_date', 'end_date', 'institution')
    search_fields = ('profile__name', 'institution', 'degree', 'field_of_study', 'description')
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('profile', 'institution', 'degree', 'field_of_study')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date'),
            'description': 'Leave end date empty for ongoing education'
        }),
        ('Additional Details', {
            'fields': ('grade', 'description'),
            'classes': ('collapse',)
        }),
    )
    
    def is_current(self, obj):
        """Display if education is currently ongoing"""
        return obj.end_date is None
    is_current.boolean = True
    is_current.short_description = 'Ongoing'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('profile')
