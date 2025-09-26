
from django.contrib import admin
from django.urls import path, include
from clergy_registration import views
from ParishRestructure import urls
from django.conf.urls.static import static
from django.conf import settings
from . import views as admin_views
from .admin import admin_site  # Import our custom admin site



urlpatterns = [
    path('', admin_views.landing_page, name='landing'),
    path('admin/', admin_site.urls),  # Use our custom admin site
    path('accounts/', include('users.urls')),
    path('clergy/', include('clergy_registration.urls')),
    path('transfer/',include("transfer.urls")),
    path('dashboard/', admin_views.centralized_dashboard, name='centralized_dashboard'),
    path('analytics/', admin_views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/export/', admin_views.export_analytics_data, name='export_analytics_data'),
    path('export/', admin_views.export_data, name='export_data'),
    path('export/bulk/', admin_views.bulk_export_data, name='bulk_export_data'),
    path('api/dashboard-stats/', admin_views.dashboard_stats_api, name='dashboard_stats_api'),
    path('parish/', include('ParishRestructure.urls')),
    
    
    
    
    
    

    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
