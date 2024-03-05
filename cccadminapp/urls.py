
from django.contrib import admin
from django.urls import path, include
from clergy_registration import views
from ParishRestructure import urls



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ParishRestructure.urls')),
    path('', include('clergy_registration.urls')),

    
]
