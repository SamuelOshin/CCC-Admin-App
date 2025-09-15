"""
Dashboard Template Tags for CCC Administrative Application

These template tags provide helper functions for the centralized dashboard system,
including navigation helpers, permission checks, and UI utilities.
"""

from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe
from django.contrib.auth.models import Group
import re

register = template.Library()


@register.filter
def is_active_url(request, url_name):
    """
    Check if the current request matches the given URL name.
    Usage: {% if request|is_active_url:'dashboard' %}active{% endif %}
    """
    try:
        from django.urls import resolve
        current_url_name = resolve(request.path_info).url_name
        return current_url_name == url_name
    except:
        return False


@register.filter
def has_permission(user, permission_name):
    """
    Check if user has a specific permission or is in a specific group.
    Usage: {% if user|has_permission:'Clergyadmin' %}
    """
    if user.is_superuser:
        return True
    
    if user.groups.filter(name=permission_name).exists():
        return True
        
    return False


@register.filter
def get_app_from_path(path):
    """
    Extract app name from URL path.
    Usage: {{ request.path_info|get_app_from_path }}
    """
    if path.startswith('/clergy/'):
        return 'clergy'
    elif path.startswith('/transfer/'):
        return 'transfer'
    elif path.startswith('/accounts/'):
        return 'accounts'
    else:
        return 'parish'


@register.simple_tag
def url_exists(url_name, *args, **kwargs):
    """
    Check if a URL name exists and can be reversed.
    Usage: {% url_exists 'dashboard' as url_valid %}
    """
    try:
        reverse(url_name, args=args, kwargs=kwargs)
        return True
    except NoReverseMatch:
        return False


@register.simple_tag
def safe_url(url_name, *args, **kwargs):
    """
    Safely reverse a URL, returning '#' if it fails.
    Usage: {% safe_url 'dashboard' %}
    """
    try:
        return reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return '#'


@register.inclusion_tag('base/partials/navigation_item.html')
def navigation_item(name, url_name, icon, description='', is_active=False):
    """
    Render a navigation item with proper styling.
    Usage: {% navigation_item 'Dashboard' 'dashboard' 'fas fa-tachometer-alt' %}
    """
    try:
        url = reverse(url_name)
    except NoReverseMatch:
        url = '#'
    
    return {
        'name': name,
        'url': url,
        'icon': icon,
        'description': description,
        'is_active': is_active,
        'is_disabled': url == '#'
    }


@register.inclusion_tag('base/partials/breadcrumb_item.html')
def breadcrumb_item(name, url=None, is_current=False):
    """
    Render a breadcrumb item.
    Usage: {% breadcrumb_item 'Home' '/' %}
    """
    return {
        'name': name,
        'url': url,
        'is_current': is_current
    }


@register.filter
def module_color(app_name):
    """
    Get the color scheme for a specific app module.
    Usage: {{ current_app|module_color }}
    """
    colors = {
        'clergy': 'primary',
        'transfer': 'success', 
        'parish': 'info',
        'accounts': 'secondary'
    }
    return colors.get(app_name, 'secondary')


@register.filter
def permission_badge(user):
    """
    Generate a permission badge for the user.
    Usage: {{ user|permission_badge }}
    """
    if user.is_superuser:
        return mark_safe('<span class="badge bg-danger">Super Admin</span>')
    
    groups = user.groups.all()
    if groups:
        group_name = groups.first().name
        color_map = {
            'Clergyadmin': 'primary',
            'TransferAdmin': 'success',
            'ParishAdmin': 'info'
        }
        color = color_map.get(group_name, 'secondary')
        return mark_safe(f'<span class="badge bg-{color}">{group_name}</span>')
    
    return mark_safe('<span class="badge bg-light text-dark">User</span>')


@register.simple_tag
def user_initials(user):
    """
    Get user initials for avatar display.
    Usage: {% user_initials user %}
    """
    if user.first_name and user.last_name:
        return f"{user.first_name[0]}{user.last_name[0]}".upper()
    elif user.first_name:
        return user.first_name[0].upper()
    elif user.username:
        return user.username[0].upper()
    else:
        return 'U'


@register.filter
def truncate_smart(value, length=50):
    """
    Smart truncation that tries to break at word boundaries.
    Usage: {{ long_text|truncate_smart:30 }}
    """
    if len(value) <= length:
        return value
    
    truncated = value[:length].rsplit(' ', 1)[0]
    return f"{truncated}..."


@register.simple_tag
def dashboard_stats(app_name):
    """
    Get dashboard statistics for an app.
    Usage: {% dashboard_stats 'clergy' as stats %}
    """
    # This would typically fetch real statistics from the database
    # For now, returning placeholder values
    stats = {
        'clergy': {
            'total': 150,
            'active': 142,
            'recent': 8,
            'pending': 3
        },
        'transfer': {
            'total': 45,
            'active': 40,
            'recent': 5,
            'pending': 2
        },
        'parish': {
            'total': 85,
            'active': 78,
            'recent': 7,
            'pending': 4
        }
    }
    return stats.get(app_name, {'total': 0, 'active': 0, 'recent': 0, 'pending': 0})


@register.filter
def highlight_search(text, search_term):
    """
    Highlight search terms in text.
    Usage: {{ description|highlight_search:search_query }}
    """
    if not search_term or not text:
        return text
    
    highlighted = re.sub(
        f'({re.escape(search_term)})',
        r'<mark class="bg-warning">\1</mark>',
        text,
        flags=re.IGNORECASE
    )
    return mark_safe(highlighted)


@register.simple_tag
def get_notification_count(user):
    """
    Get notification count for user (placeholder).
    Usage: {% get_notification_count user as count %}
    """
    # This would typically query a notifications model
    # For now, returning a placeholder value
    return 0


@register.filter
def format_file_size(bytes_value):
    """
    Format file size in human readable format.
    Usage: {{ file.size|format_file_size }}
    """
    try:
        bytes_value = int(bytes_value)
    except (ValueError, TypeError):
        return '0 B'
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"


@register.simple_tag(takes_context=True)
def active_class(context, url_name, class_name='active'):
    """
    Return CSS class if URL is active.
    Usage: {% active_class 'dashboard' 'current-page' %}
    """
    request = context.get('request')
    if request and is_active_url(request, url_name):
        return class_name
    return ''


@register.filter
def dict_get(dictionary, key):
    """
    Get value from dictionary by key.
    Usage: {{ my_dict|dict_get:key_variable }}
    """
    try:
        return dictionary.get(key)
    except AttributeError:
        return None


@register.simple_tag
def version_info():
    """
    Get application version information.
    Usage: {% version_info %}
    """
    return {
        'version': '1.0.0',
        'build': 'stable',
        'release_date': '2024-01-01'
    }


@register.inclusion_tag('base/partials/loading_spinner.html')
def loading_spinner(size='md', text='Loading...'):
    """
    Render a loading spinner.
    Usage: {% loading_spinner 'lg' 'Please wait...' %}
    """
    return {
        'size': size,
        'text': text
    }
