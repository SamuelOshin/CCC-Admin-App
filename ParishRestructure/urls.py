from django.urls import path, include
from django.conf.urls import handler404, handler500, handler403, handler400
from . import views
from django.conf.urls.static import static
from django.conf import settings
#For api
from .views import ParishDirectoryViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'parish', ParishDirectoryViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('restrucutre/', views.restructure_parish, name='add_parish'),
    path('parish_dashboard/', views.parish_dashboard, name='parish_dashboard'),
    path('location/', views.add_location, name='add_location'),
    path('view_parishes/', views.view_parishes, name='view_parishes'),
    path('edit_parish/<int:pk>/', views.edit_parish, name='edit_parish'),   
    path('delete_parish/<int:pk>/', views.delete_parish, name='delete_parish'),
    path('get_regions_and_areas/', views.get_regions_and_areas, name='get_regions_and_areas'),
    path('view_parish/<int:pk>/', views.view_parish, name='view_parish'),
    path('view/<int:pk>/', views.view_parishh, name='view_parishh'),
    path('register/', views.reg_parish, name='parish-registration'),
    path('all_parish/' , views.all_parish, name='all-parish'),
    path('edit/<int:pk>/', views.edit_parish_reg, name='edit-parish'),
    path('register0/', views.regparish, name='reg-old-parish'),
    path('approval_queue/', views.approval_queue, name='approval_queue'),  # for admin only
    path('approve/<int:pk>/', views.accept_parish_registration, name='approve'),  # for admin only
    path('reject/<int:pk>/', views.reject_parish_registration, name='reject'),  # for admin only
    path('view-regparish/<int:pk>/', views.view_regparish, name='view-parish'),
    path('approved/', views.approved, name='approved'), 
    path('editreg_parish/<int:pk>', views.edit_reg_parish, name='edit_regparish')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Handling 404 and 500 errors
# handler404 = 'django.http.views.page_not_found'
# handler500 = 'django.http.views.server_error'

