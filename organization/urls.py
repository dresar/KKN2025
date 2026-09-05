from django.urls import path
from . import views, api_views

app_name = 'organization'

urlpatterns = [
    # Dashboard Organisasi Admin
    path('', views.organization_admin, name='organization_admin'),
    
    # Perangkat Desa URLs
    path('perangkat/', views.perangkat_list, name='perangkat_list'),
    path('perangkat/add/', views.perangkat_add, name='perangkat_add'),
    path('perangkat/<int:pk>/edit/', views.perangkat_edit, name='perangkat_edit'),
    path('perangkat/<int:pk>/delete/', views.perangkat_delete, name='perangkat_delete'),
    path('perangkat/<int:pk>/', views.perangkat_detail, name='perangkat_detail'),
    
    # Lembaga Adat URLs
    path('lembaga-adat/', views.lembaga_adat_list, name='lembaga_adat_list'),
    path('lembaga-adat/add/', views.lembaga_adat_add, name='lembaga_adat_add'),
    path('lembaga-adat/<int:pk>/edit/', views.lembaga_adat_edit, name='lembaga_adat_edit'),
    path('lembaga-adat/<int:pk>/delete/', views.lembaga_adat_delete, name='lembaga_adat_delete'),
    path('lembaga-adat/<int:pk>/', views.lembaga_adat_detail, name='lembaga_adat_detail'),
    
    # Penggerak PKK URLs
    path('penggerak-pkk/', views.penggerak_pkk_list, name='penggerak_pkk_list'),
    path('penggerak-pkk/add/', views.penggerak_pkk_add, name='penggerak_pkk_add'),
    path('penggerak-pkk/<int:pk>/edit/', views.penggerak_pkk_edit, name='penggerak_pkk_edit'),
    path('penggerak-pkk/<int:pk>/delete/', views.penggerak_pkk_delete, name='penggerak_pkk_delete'),
    path('penggerak-pkk/<int:pk>/', views.penggerak_pkk_detail, name='penggerak_pkk_detail'),
    
    # Kepemudaan URLs
    path('kepemudaan/', views.kepemudaan_list, name='kepemudaan_list'),
    path('kepemudaan/add/', views.kepemudaan_add, name='kepemudaan_add'),
    path('kepemudaan/<int:pk>/edit/', views.kepemudaan_edit, name='kepemudaan_edit'),
    path('kepemudaan/<int:pk>/delete/', views.kepemudaan_delete, name='kepemudaan_delete'),
    path('kepemudaan/<int:pk>/', views.kepemudaan_detail, name='kepemudaan_detail'),
    
    # Karang Taruna URLs
    path('karang-taruna/', views.karang_taruna_list, name='karang_taruna_list'),
    path('karang-taruna/add/', views.karang_taruna_add, name='karang_taruna_add'),
    path('karang-taruna/<int:pk>/edit/', views.karang_taruna_edit, name='karang_taruna_edit'),
    path('karang-taruna/<int:pk>/delete/', views.karang_taruna_delete, name='karang_taruna_delete'),
    path('karang-taruna/<int:pk>/', views.karang_taruna_detail, name='karang_taruna_detail'),
    
    # API untuk choices
    path('api/penduduk-choices/', views.api_penduduk_choices, name='api_penduduk_choices'),
    
    # API endpoints untuk CRUD operations
    # Perangkat Desa API
    path('api/perangkat-desa/', views.api_perangkat_desa_list, name='api_perangkat_desa_list'),
    path('api/perangkat-desa/<int:pk>/', views.api_perangkat_desa_detail, name='api_perangkat_desa_detail'),
    path('api/perangkat-desa/create/', views.api_perangkat_desa_create, name='api_perangkat_desa_create'),
    path('api/perangkat-desa/<int:pk>/update/', views.api_perangkat_desa_update, name='api_perangkat_desa_update'),
    path('api/perangkat-desa/<int:pk>/delete/', views.api_perangkat_desa_delete, name='api_perangkat_desa_delete'),
    
    # Lembaga Adat API
    path('api/lembaga-adat/', views.api_lembaga_adat_list, name='api_lembaga_adat_list'),
    path('api/lembaga-adat/<int:pk>/', views.api_lembaga_adat_detail, name='api_lembaga_adat_detail'),
    path('api/lembaga-adat/create/', views.api_lembaga_adat_create, name='api_lembaga_adat_create'),
    path('api/lembaga-adat/<int:pk>/update/', views.api_lembaga_adat_update, name='api_lembaga_adat_update'),
    path('api/lembaga-adat/<int:pk>/delete/', views.api_lembaga_adat_delete, name='api_lembaga_adat_delete'),
    
    # Penggerak PKK API
    path('api/penggerak-pkk/', views.api_penggerak_pkk_list, name='api_penggerak_pkk_list'),
    path('api/penggerak-pkk/<int:pk>/', views.api_penggerak_pkk_detail, name='api_penggerak_pkk_detail'),
    path('api/penggerak-pkk/create/', views.api_penggerak_pkk_create, name='api_penggerak_pkk_create'),
    path('api/penggerak-pkk/<int:pk>/update/', views.api_penggerak_pkk_update, name='api_penggerak_pkk_update'),
    path('api/penggerak-pkk/<int:pk>/delete/', views.api_penggerak_pkk_delete, name='api_penggerak_pkk_delete'),
    
    # Kepemudaan API
    path('api/kepemudaan/', views.api_kepemudaan_list, name='api_kepemudaan_list'),
    path('api/kepemudaan/<int:pk>/', views.api_kepemudaan_detail, name='api_kepemudaan_detail'),
    path('api/kepemudaan/create/', views.api_kepemudaan_create, name='api_kepemudaan_create'),
    path('api/kepemudaan/<int:pk>/update/', views.api_kepemudaan_update, name='api_kepemudaan_update'),
    path('api/kepemudaan/<int:pk>/delete/', views.api_kepemudaan_delete, name='api_kepemudaan_delete'),
    
    # Karang Taruna API
    path('api/karang-taruna/', views.api_karang_taruna_list, name='api_karang_taruna_list'),
    path('api/karang-taruna/<int:pk>/', views.api_karang_taruna_detail, name='api_karang_taruna_detail'),
    path('api/karang-taruna/create/', views.api_karang_taruna_create, name='api_karang_taruna_create'),
    path('api/karang-taruna/<int:pk>/update/', views.api_karang_taruna_update, name='api_karang_taruna_update'),
    path('api/karang-taruna/<int:pk>/delete/', views.api_karang_taruna_delete, name='api_karang_taruna_delete'),
]