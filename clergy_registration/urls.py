from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    
    path('register/', views.register_clergy , name='register_clergy'),
    path('', views.dashboard, name='dashboard'),
    path('all_clergy', views.all_clergy, name="all_clergy"),
    path('<int:id>', views.view_clergy, name='view_clergy'),
    path('save/<int:id>', views.view_profile, name='view_profile'),
    path('edit/<int:id>', views.edit_clergy, name='edit_clergy'),
    path('delete/<int:id>', views.delete_clergy, name='delete_clergy'),
    path('view-annointments/<int:id>', views.view_and_add_annointment, name='view-and-add-annointment'),
    path('clergy/<int:id>/pdf/', views.generate_clergy_pdf, name='generate_clergy_pdf'),
    
    # path('submit/', views.handle_clergy_registration, name='submit_form'),

    # Define more URL patterns as needed
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
