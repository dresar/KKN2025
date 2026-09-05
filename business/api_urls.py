from django.urls import path
from . import api_views

app_name = 'business_api'

urlpatterns = [
    # Statistics
    path('api/stats/', api_views.api_stats, name='stats'),
    
    # Businesses
    path('api/businesses/', api_views.api_businesses, name='businesses'),
    path('api/businesses/<int:business_id>/', api_views.api_business_detail, name='business_detail'),
    
    # Koperasi API
    path('api/koperasi/', api_views.api_koperasi_list, name='api_koperasi_list'),
    
    # BUMG API
    path('api/bumg/', api_views.api_bumg_list, name='api_bumg_list'),
    
    # UKM API
    path('api/ukm/', api_views.api_ukm_list, name='api_ukm_list'),
    
    # Aset API
    path('api/aset/', api_views.api_aset_list, name='api_aset_list'),
    
    # Layanan Jasa API
    path('api/jasa/', api_views.api_jasa_list, name='api_jasa_list'),
]