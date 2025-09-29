from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin.sites import AdminSite
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.sites import UnfoldAdminSite


class CustomAdminSite(UnfoldAdminSite):
    """
    Custom admin site with enhanced dashboard and branding
    """
    site_header = "CCC Administrative Management System"
    site_title = "CCC Admin Portal"
    index_title = "Welcome to CCC Administration"
    index_template = "admin/index.html"  # Use our custom template
    site_url = None

    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all installed apps and models for the admin index.
        """
        app_list = super().get_app_list(request, app_label)

        # Custom ordering of apps
        app_order = [
            'clergy_registration',
            'ParishRestructure',
            'transfer',
            'users',
            'auth',
        ]

        # Sort apps according to our custom order
        app_list.sort(key=lambda x: app_order.index(x['app_label']) if x['app_label'] in app_order else len(app_order))

        return app_list

    def index(self, request, extra_context=None):
        """
        Display the main admin index page with custom dashboard.
        """
        extra_context = extra_context or {}

        # Add custom context for the dashboard
        extra_context.update({
            'dashboard_title': 'CCC Administrative Dashboard',
            'dashboard_subtitle': 'Comprehensive Church Administration Management',
            'show_dashboard': True,
        })

        return super().index(request, extra_context)


# Create the custom admin site instance
admin_site = CustomAdminSite(name='ccc_admin')

# Register the custom admin site
admin.site = admin_site

# Register all models with the custom admin site
from clergy_registration.models import ClergyDetails, AnnointmentGazzette
from ParishRestructure.models import Location, ParishRestructure, ParishRegistration, ParishDirectory
from transfer.models import PostingHistory, ClergyTrfbio, TransferData
from users.models import UserProfile
from users.admin import CustomUserAdmin
from django.contrib.auth.models import Group, User

# Register models with the custom admin site
admin_site.register(ClergyDetails)
admin_site.register(AnnointmentGazzette)
admin_site.register(Location)
admin_site.register(ParishRestructure)
admin_site.register(ParishRegistration)
admin_site.register(ParishDirectory)
admin_site.register(PostingHistory)
admin_site.register(ClergyTrfbio)
admin_site.register(TransferData)
admin_site.register(UserProfile)
admin_site.register(Group)
admin_site.register(User, CustomUserAdmin)