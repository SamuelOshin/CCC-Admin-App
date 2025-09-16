"""
Dashboard Context Processor for CCC Administrative Application

This module provides context for the centralized dashboard system,
determining the current app, navigation items, and user permissions
based on the request URL and user groups.
"""

from django.urls import resolve, reverse, NoReverseMatch
from django.contrib.auth.models import Group


def dashboard_context(request):
    """
    Provides dashboard navigation context based on current URL and user permissions.
    
    Args:
        request: HttpRequest object
        
    Returns:
        dict: Context dictionary with navigation and app information
    """
    
    # Navigation configuration for each app module
    NAVIGATION_CONFIG = {
        'centralized': {
            'name': 'Centralized Dashboard',
            'icon': 'fas fa-tachometer-alt',
            'color': 'primary',
            'permission_group': None,  # Available to all authenticated users
            'items': [
                {
                    'name': 'System Overview',
                    'url_name': 'centralized_dashboard',
                    'icon': 'fas fa-chart-line',
                    'description': 'Comprehensive system dashboard'
                },
            ]
        },
        'clergy': {
            'name': 'Clergy Management',
            'icon': 'fas fa-users',
            'color': 'primary',
            'permission_group': 'clergyadmin',
            'items': [
                {
                    'name': 'Dashboard',
                    'url_name': 'dashboard',
                    'icon': 'fas fa-tachometer-alt',
                    'description': 'Clergy management overview'
                },
                {
                    'name': 'Register Clergy',
                    'url_name': 'register_clergy',
                    'icon': 'fas fa-user-plus',
                    'description': 'Add new clergy member'
                },
                {
                    'name': 'Clergy Directory',
                    'url_name': 'all_clergy',
                    'icon': 'fas fa-list',
                    'description': 'View all clergy members'
                },
            ]
        },
        'transfer': {
            'name': 'Transfer Management',
            'icon': 'fas fa-exchange-alt', 
            'color': 'success',
            'permission_group': 'transferadmin',
            'items': [
                {
                    'name': 'Dashboard', 
                    'url_name': 't_dashboard', 
                    'icon': 'fas fa-tachometer-alt',
                    'description': 'Transfer management overview'
                },
                {
                    'name': 'New Transfer', 
                    'url_name': 'clergy', 
                    'icon': 'fas fa-arrow-right',
                    'description': 'Create clergy transfer'
                },
                {
                    'name': 'Transfer History', 
                    'url_name': 'trfTable', 
                    'icon': 'fas fa-history',
                    'description': 'View recent transfers'
                },
            ]
        },
        'parish': {
            'name': 'Parish Management',
            'icon': 'fas fa-church',
            'color': 'info',
            'permission_group': 'parishadmin',  # Users in parishadmin group
            'items': [
                {
                    'name': 'Dashboard', 
                    'url_name': 'parish_dashboard', 
                    'icon': 'fas fa-tachometer-alt',
                    'description': 'Parish management overview'
                },
                {
                    'name': 'Parish Directory', 
                    'url_name': 'all-parish', 
                    'icon': 'fas fa-list',
                    'description': 'View all parishes'
                },
                {
                    'name': 'Restructure', 
                    'url_name': 'add_parish', 
                    'icon': 'fas fa-sitemap',
                    'description': 'Restructure parish boundaries'
                },
                {
                    'name': 'Register Parish', 
                    'url_name': 'parish-registration', 
                    'icon': 'fas fa-plus',
                    'description': 'Register new parish'
                },
                {
                    'name': 'Approval Queue', 
                    'url_name': 'approval_queue', 
                    'icon': 'fas fa-clock',
                    'description': 'Pending parish registrations'
                },
                {
                    'name': 'Approved Parishes', 
                    'url_name': 'approved', 
                    'icon': 'fas fa-check-circle',
                    'description': 'Approved parish registrations'
                },
            ]
        }
    }
    
    context = {
        'current_app': None,
        'current_module': None,
        'navigation_items': [],
        'all_modules': [],
        'breadcrumb': [],
        'user_permissions': {},
        'app_title': 'CCC Admin App',
        'dashboard_config': NAVIGATION_CONFIG,
    }
    
    # Only process for authenticated users
    if not request.user.is_authenticated:
        return context
        
    # Determine current app from URL path
    try:
        current_url_name = resolve(request.path_info).url_name
        path_parts = request.path_info.strip('/').split('/')
        
        # Determine current app based on URL patterns
        if request.path_info == '/dashboard/':
            current_app = 'centralized'
        elif request.path_info.startswith('/clergy/'):
            current_app = 'clergy'
        elif request.path_info.startswith('/transfer/'):
            current_app = 'transfer'
        elif request.path_info.startswith('/accounts/'):
            current_app = 'accounts'
        else:
            # Parish app is at root level
            current_app = 'parish'
            
    except Exception:
        current_app = 'parish'  # Default fallback
        current_url_name = None
    
    # Get user permissions
    user_groups = list(request.user.groups.values_list('name', flat=True))
    is_superuser = request.user.is_superuser
    
    context.update({
        'current_app': current_app,
        'current_url_name': current_url_name,
        'user_groups': user_groups,
        'is_superuser': is_superuser,
    })
    
    # Determine available modules based on user permissions
    available_modules = []
    
    for module_key, module_config in NAVIGATION_CONFIG.items():
        permission_group = module_config.get('permission_group')
        has_permission = False
        
        if is_superuser:
            has_permission = True
        elif module_key == 'centralized':
            # Centralized dashboard is available to all authenticated users
            has_permission = True
        elif permission_group is None:
            # Parish app: accessible to users NOT in clergyadmin group
            has_permission = 'clergyadmin' not in user_groups
        elif permission_group in user_groups:
            has_permission = True
            
        if has_permission:
            # Build navigation items with accessible URLs
            nav_items = []
            for item in module_config['items']:
                try:
                    # Try to build URL and verify access
                    url = reverse(item['url_name'])
                    nav_items.append({
                        'name': item['name'],
                        'url': url,
                        'url_name': item['url_name'],
                        'icon': item['icon'],
                        'description': item.get('description', ''),
                        'is_active': current_url_name == item['url_name']
                    })
                except NoReverseMatch:
                    # Skip items with invalid URLs
                    continue
                    
            if nav_items:  # Only add module if it has accessible items
                module_info = {
                    'key': module_key,
                    'name': module_config['name'],
                    'icon': module_config['icon'],
                    'color': module_config['color'],
                    'items': nav_items,
                    'is_current': current_app == module_key
                }
                available_modules.append(module_info)
    
    context['all_modules'] = available_modules
    
    # Set current module navigation
    if current_app and current_app in [m['key'] for m in available_modules]:
        current_module = next(m for m in available_modules if m['key'] == current_app)
        context.update({
            'current_module': current_module,
            'navigation_items': current_module['items'],
        })
    
    # Generate breadcrumb trail
    breadcrumb = [{'name': 'Home', 'url': '/'}]
    
    if current_app and current_app in NAVIGATION_CONFIG:
        module_config = NAVIGATION_CONFIG[current_app]
        breadcrumb.append({
            'name': module_config['name'],
            'url': '#',
            'is_current': True
        })
        
        # Add specific page if not dashboard
        if current_url_name and current_url_name not in ['dashboard', 't_dashboard', 'parish_dashboard',  'centralized_dashboard']:
            # Find current page name from navigation items
            for item in context.get('navigation_items', []):
                if item['url_name'] == current_url_name:
                    breadcrumb.append({
                        'name': item['name'],
                        'url': item['url'],
                        'is_current': True
                    })
                    breadcrumb[-2]['is_current'] = False  # Module is no longer current
                    break
    
    context['breadcrumb'] = breadcrumb
    
    # Add user permission summary
    context['user_permissions'] = {
        'can_manage_clergy': 'clergyadmin' in user_groups or is_superuser,
        'can_manage_transfers': 'transferadmin' in user_groups or is_superuser,
        'can_manage_parishes': 'parishadmin' in user_groups or is_superuser,
        'is_superuser': is_superuser,
        'groups': user_groups,
    }
    
    return context
