from django.contrib import admin
from django.db.models import Count
from .models import Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """
    Admin configuration for Skill model
    """
    list_display = [
        'name', 'profile', 'level', 'category', 'level_display'
    ]
    list_filter = [
        'level', 'category', 'profile'
    ]
    search_fields = [
        'name', 'category', 'profile__name', 'profile__email'
    ]
    ordering = ['category', 'name']
    readonly_fields = ['id']
    list_editable = ['level', 'category']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('profile', 'name', 'level')
        }),
        ('Categorization', {
            'fields': ('category',),
            'description': 'Group skills by category (e.g., Programming, Design, Soft Skills)'
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related('profile')
    
    def level_display(self, obj):
        """
        Display human-readable level
        """
        return obj.get_level_display()
    level_display.short_description = 'Level (Display)'
    level_display.admin_order_field = 'level'
    
    # Custom actions
    actions = [
        'mark_as_beginner', 'mark_as_intermediate', 
        'mark_as_advanced', 'mark_as_expert',
        'categorize_as_programming', 'categorize_as_design'
    ]
    
    def mark_as_beginner(self, request, queryset):
        """Mark selected skills as beginner level"""
        updated = queryset.update(level='beginner')
        self.message_user(request, f'{updated} skills marked as beginner level.')
    mark_as_beginner.short_description = "Mark selected skills as beginner"
    
    def mark_as_intermediate(self, request, queryset):
        """Mark selected skills as intermediate level"""
        updated = queryset.update(level='intermediate')
        self.message_user(request, f'{updated} skills marked as intermediate level.')
    mark_as_intermediate.short_description = "Mark selected skills as intermediate"
    
    def mark_as_advanced(self, request, queryset):
        """Mark selected skills as advanced level"""
        updated = queryset.update(level='advanced')
        self.message_user(request, f'{updated} skills marked as advanced level.')
    mark_as_advanced.short_description = "Mark selected skills as advanced"
    
    def mark_as_expert(self, request, queryset):
        """Mark selected skills as expert level"""
        updated = queryset.update(level='expert')
        self.message_user(request, f'{updated} skills marked as expert level.')
    mark_as_expert.short_description = "Mark selected skills as expert"
    
    def categorize_as_programming(self, request, queryset):
        """Categorize selected skills as Programming"""
        updated = queryset.update(category='Programming')
        self.message_user(request, f'{updated} skills categorized as Programming.')
    categorize_as_programming.short_description = "Categorize as Programming"
    
    def categorize_as_design(self, request, queryset):
        """Categorize selected skills as Design"""
        updated = queryset.update(category='Design')
        self.message_user(request, f'{updated} skills categorized as Design.')
    categorize_as_design.short_description = "Categorize as Design"
    
    def changelist_view(self, request, extra_context=None):
        """
        Add summary statistics to the changelist view
        """
        response = super().changelist_view(request, extra_context=extra_context)
        
        try:
            qs = response.context_data['cl'].queryset
            summary = {
                'total_skills': qs.count(),
                'level_stats': dict(qs.values_list('level').annotate(Count('level'))),
                'category_stats': dict(qs.exclude(category='').values_list('category').annotate(Count('category'))[:5]),
            }
            response.context_data['summary'] = summary
        except (AttributeError, KeyError):
            pass
            
        return response
