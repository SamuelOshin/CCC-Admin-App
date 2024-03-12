
from django.contrib import admin
from django.urls import path, include
from clergy_registration import views
from ParishRestructure import urls
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('clergy/', include('clergy_registration.urls')),
    path('', include('ParishRestructure.urls')),
    
    
    
    
    
    

    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
