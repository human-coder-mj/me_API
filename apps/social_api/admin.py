from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import SocialLink


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    """
    Admin configuration for SocialLink model
    """
    list_display = [
        'profile', 'link_type_display', 'display_name', 
        'clickable_url', 'link_type'
    ]
    list_filter = [
        'link_type', 'profile'
    ]
    search_fields = [
        'display_name', 'url', 'profile__name', 'profile__email'
    ]
    ordering = ['profile__name', 'link_type']
    readonly_fields = ['id']
    list_editable = ['display_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('profile', 'link_type', 'url')
        }),
        ('Display Options', {
            'fields': ('display_name',),
            'description': 'Optional custom name for the link (defaults to platform name)'
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related('profile')
    
    def link_type_display(self, obj):
        """
        Display human-readable link type
        """
        return obj.get_link_type_display()
    link_type_display.short_description = 'Platform'
    link_type_display.admin_order_field = 'link_type'
    
    def display_name_or_url(self, obj):
        """
        Show display name if available, otherwise show URL
        """
        return obj.display_name or obj.url[:50] + ('...' if len(obj.url) > 50 else '')
    display_name_or_url.short_description = 'Display Name / URL'
    
    def clickable_url(self, obj):
        """
        Make URL clickable in admin
        """
        if obj.url:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">🔗 Open</a>',
                obj.url
            )
        return '-'
    clickable_url.short_description = 'Link'
    clickable_url.allow_tags = True
    
    # Custom actions
    actions = [
        'set_type_github', 'set_type_linkedin', 'set_type_portfolio',
        'set_type_website', 'clear_display_names'
    ]
    
    def set_type_github(self, request, queryset):
        """Set selected links as GitHub"""
        updated = queryset.update(link_type='github')
        self.message_user(request, f'{updated} links set as GitHub.')
    set_type_github.short_description = "Set as GitHub links"
    
    def set_type_linkedin(self, request, queryset):
        """Set selected links as LinkedIn"""
        updated = queryset.update(link_type='linkedin')
        self.message_user(request, f'{updated} links set as LinkedIn.')
    set_type_linkedin.short_description = "Set as LinkedIn links"
    
    def set_type_portfolio(self, request, queryset):
        """Set selected links as Portfolio"""
        updated = queryset.update(link_type='portfolio')
        self.message_user(request, f'{updated} links set as Portfolio.')
    set_type_portfolio.short_description = "Set as Portfolio links"
    
    def set_type_website(self, request, queryset):
        """Set selected links as Website"""
        updated = queryset.update(link_type='website')
        self.message_user(request, f'{updated} links set as Website.')
    set_type_website.short_description = "Set as Website links"
    
    def clear_display_names(self, request, queryset):
        """Clear display names for selected links"""
        updated = queryset.update(display_name='')
        self.message_user(request, f'Display names cleared for {updated} links.')
    clear_display_names.short_description = "Clear display names"
    
    def changelist_view(self, request, extra_context=None):
        """
        Add summary statistics to the changelist view
        """
        response = super().changelist_view(request, extra_context=extra_context)
        
        try:
            qs = response.context_data['cl'].queryset
            
            # Platform distribution
            platform_stats = dict(qs.values_list('link_type').annotate(Count('link_type')))
            platform_display = {}
            for link_type, count in platform_stats.items():
                display_name = dict(SocialLink.LINK_TYPES).get(link_type, link_type.title())
                platform_display[display_name] = count
            
            summary = {
                'total_links': qs.count(),
                'profiles_count': qs.values('profile').distinct().count(),
                'platform_stats': platform_display,
                'links_with_display_names': qs.exclude(display_name='').count(),
            }
            response.context_data['summary'] = summary
        except (AttributeError, KeyError):
            pass
            
        return response
