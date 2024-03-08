
from django.contrib import admin
from django.urls import path, include
from clergy_registration import views
from ParishRestructure import urls
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    path('clergy/', include('clergy_registration.urls')),
    path('admin/', admin.site.urls),
    path('', include('ParishRestructure.urls')),
    

    
]


urlpatterns += staticfiles_urlpatterns()
