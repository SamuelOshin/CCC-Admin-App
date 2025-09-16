from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.first_time_password_change, name='first_time_password_change'),
    
]
