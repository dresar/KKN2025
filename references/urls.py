from django.urls import path, include
from . import views

app_name = 'references'

# Admin URL patterns
admin_patterns = [
    path('', views.references_admin, name='references_admin'),
    path('dusun/', views.dusun_admin, name='dusun_admin'),
    path('dusun/add/', views.add_dusun, name='admin_add_dusun'),
    path('dusun/edit/<int:pk>/', views.edit_dusun, name='admin_edit_dusun'),
    path('lorong/', views.lorong_admin, name='lorong_admin'),
    path('penduduk/', views.penduduk_admin, name='penduduk_admin'),
    path('penduduk/add/', views.add_penduduk_new, name='add_penduduk'),
    path('penduduk/addpenduduk/', views.add_penduduk_new, name='add_penduduk_new'),
    path('penduduk/edit/<int:pk>/', views.edit_penduduk, name='edit_penduduk'),
    path('disabilitas/', views.disabilitas_admin, name='disabilitas_admin'),
    path('family/', views.family_admin, name='family_admin'),
]

# Admin API patterns (with authentication)
admin_api_patterns = [
    # Admin API endpoints for AJAX operations
    path('penduduk/', views.penduduk_list_api, name='admin_penduduk_list'),
    path('penduduk/<int:pk>/', views.penduduk_detail_api, name='admin_penduduk_detail'),
    path('penduduk/create/', views.penduduk_create_api, name='admin_penduduk_create'),
    path('penduduk/count/', views.penduduk_count_api, name='admin_penduduk_count'),
    
    # Dusun Admin APIs
    path('dusun/', views.dusun_list_api, name='admin_dusun_list'),
    path('dusun/<int:pk>/', views.dusun_detail_api, name='admin_dusun_detail'),
    path('dusun/create/', views.dusun_create_api, name='admin_dusun_create'),
    
    # Lorong Admin APIs
    path('lorong/', views.lorong_list_api, name='admin_lorong_list'),
    path('lorong/<int:pk>/', views.lorong_detail_api, name='admin_lorong_detail'),
    path('lorong/create/', views.lorong_create_api, name='admin_lorong_create'),
    
    # Family Admin APIs
    path('family/', views.family_list_api, name='admin_family_list'),
    path('family/<int:pk>/', views.family_detail_api, name='admin_family_detail'),
    path('family/create/', views.family_create_api, name='admin_family_create'),
    
    # Export/Import Admin APIs
    path('export/<str:model_type>/', views.export_data, name='admin_export_data'),
    path('import/<str:model_type>/', views.import_data, name='admin_import_data'),
]

# API URL patterns
api_patterns = [
    # Test endpoint untuk debugging
    path('test/', views.api_test_endpoint, name='api_test_endpoint'),
    
    # Public APIs (no authentication required)
    path('public-stats/', views.public_stats_api, name='public_stats_api'),
    path('public-dusun/', views.public_dusun_list_api, name='public_dusun_list'),
    path('public-lorong/', views.public_lorong_list_api, name='public_lorong_list'),
    path('public-penduduk/', views.public_penduduk_list_api, name='public_penduduk_list'),
    path('public-penduduk-create/', views.public_penduduk_create_api, name='public_penduduk_create'),
    path('public-penduduk/<int:penduduk_id>/', views.public_penduduk_detail_api, name='public_penduduk_detail'),
    path('public-penduduk-update/<int:penduduk_id>/', views.public_penduduk_update_api, name='public_penduduk_update'),
    
    # Consolidated API endpoints (from former api_views.py)
    path('population/', views.api_population, name='api_population'),
    path('population/stats/', views.api_population_stats, name='api_population_stats'),
    path('population/export/', views.api_population_export, name='api_population_export'),
    path('dusun-data/', views.api_dusun, name='api_dusun'),  # Renamed to avoid conflict
    path('disability/', views.api_disability, name='api_disability'),
    
    # Statistics and Dashboard APIs
    path('stats/', views.references_stats_api, name='references_stats'),
    path('dashboard-summary/', views.dashboard_summary_api, name='dashboard_summary'),
    
    # Export/Import APIs
    path('export/<str:model_type>/', views.export_data, name='export_data'),
    path('import/<str:model_type>/', views.import_data, name='import_data'),
    
    # Main CRUD APIs
    # Penduduk APIs
    path('penduduk/', views.penduduk_list_api, name='penduduk_list'),
    path('penduduk/list/', views.penduduk_list_api, name='penduduk_list_compat'),
    path('penduduk/<int:pk>/', views.penduduk_detail_api, name='penduduk_detail'),
    path('penduduk/create/', views.penduduk_create_api, name='penduduk_create'),
    path('penduduk/bulk-delete/', views.penduduk_bulk_delete_api, name='penduduk_bulk_delete'),
    path('penduduk/search/', views.penduduk_search_api, name='penduduk_search'),
    path('penduduk/export/', views.penduduk_export_api, name='penduduk_export'),
    
    # Dusun APIs
    path('dusun/', views.dusun_list_api, name='dusun_list'),
    path('dusun/list/', views.dusun_list_api, name='dusun_list_compat'),
    path('dusun/<int:pk>/', views.dusun_detail_api, name='dusun_detail'),
    path('dusun/create/', views.dusun_create_api, name='dusun_create'),
    
    # Lorong APIs
    path('lorong/', views.lorong_list_api, name='lorong_list'),
    path('lorong/list/', views.lorong_list_api, name='lorong_list_compat'),
    path('lorong/<int:pk>/', views.lorong_detail_api, name='lorong_detail'),
    path('lorong/create/', views.lorong_create_api, name='lorong_create'),
    
    # Disabilitas APIs
    path('disabilitas-type/', views.disabilitas_type_list_api, name='disabilitas_type_list'),
    path('disabilitas-type/<int:pk>/', views.disabilitas_type_detail_api, name='disabilitas_type_detail'),
    path('disabilitas-type/create/', views.disabilitas_type_create_api, name='disabilitas_type_create'),
    
    path('disabilitas-data/', views.disabilitas_data_list_api, name='disabilitas_data_list'),
    path('disabilitas-data/<int:pk>/', views.disabilitas_data_detail_api, name='disabilitas_data_detail'),
    path('disabilitas-data/create/', views.disabilitas_data_create_api, name='disabilitas_data_create'),
    
    # Family APIs
    path('family/', views.family_list_api, name='family_list'),
    path('family/<int:pk>/', views.family_detail_api, name='family_detail'),
    path('family/create/', views.family_create_api, name='family_create')
]

urlpatterns = [
    # Main admin view
    path('', views.references_admin, name='references_admin'),
    
    # Include admin and API patterns
    path('admin/', include(admin_patterns)),
    path('admin-api/', include(admin_api_patterns)),  # Admin API endpoints
    path('api/', include(api_patterns)),
]