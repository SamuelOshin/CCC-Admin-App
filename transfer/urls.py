from django.urls import path, include
from . import views
from .views import ParishRestructureViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'parish', ParishRestructureViewSet)


urlpatterns = [
    path('clergy/<int>/transfer/api/', include(router.urls)),
    path('trfTable/', views.new_trf_table, name='trfTable'),
    path('clergy/<int:id>/', views.new_transfer, name='new_transfer'),
    path('transfer/<int:transfer_id>/update/', views.update_transfer, name='update_transfer'),
    path('clergyTable/', views.clergy_details, name='clergy'),
    path('dashboard', views.transfer_dashboard, name='t_dashboard'),
    path('postingH/<int:id>/', views.view_add_posting, name='posting'),
]