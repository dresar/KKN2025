from django.urls import path, include
from . import views

app_name = 'business'

urlpatterns = [
    # API endpoints
    path('', include('business.api_urls')),
    # CSRF Token
    path('csrf-token/', views.get_csrf_token, name='csrf_token'),
    # Business module view
    path('', views.business_module_view, name='business_admin'),
    
    # Submenu views
    path('koperasi/', views.koperasi_view, name='koperasi'),
    path('bumg/', views.bumg_view, name='bumg'),
    path('ukm/', views.ukm_view, name='ukm'),
    path('aset/', views.aset_view, name='aset'),
    path('jasa/', views.jasa_view, name='jasa'),
    
    # BusinessCategory APIs
    path('categories/', views.business_category_list, name='businesscategory_list'),
    path('categories/<int:pk>/', views.business_category_detail, name='businesscategory_detail'),
    path('categories/create/', views.business_category_create, name='businesscategory_create'),
    path('categories/<int:pk>/update/', views.business_category_update, name='businesscategory_update'),
    path('categories/<int:pk>/delete/', views.business_category_delete, name='businesscategory_delete'),
    
    # Business APIs
    path('businesses/', views.businesses_list, name='business_list'),
    path('businesses/<int:pk>/', views.business_detail, name='business_detail'),
    path('businesses/create/', views.business_create, name='business_create'),
    path('businesses/<int:pk>/update/', views.business_update, name='business_update'),
    path('businesses/<int:pk>/delete/', views.business_delete, name='business_delete'),
    
    # BusinessOwner APIs
    path('owners/', views.business_owners_list, name='businessowner_list'),
    
    # BusinessProduct APIs
    path('products/', views.business_products_list, name='businessproduct_list'),
    
    # BusinessFinance APIs
    path('finances/', views.business_finances_list, name='businessfinance_list'),
    
    # New Business Module APIs
    path('api/koperasi/', views.koperasi_api, name='koperasi_api'),
    path('api/bumg/', views.bumg_api, name='bumg_api'),
    path('api/ukm/', views.ukm_api, name='ukm_api'),
    path('api/aset/', views.aset_api, name='aset_api'),
    path('api/jasa/', views.jasa_api, name='jasa_api'),
    
    # Category Management APIs
    path('category/', views.category_view, name='category'),
    path('api/category/', views.category_api, name='category_api'),
    path('api/category/list/', views.category_list_api, name='category_list_api'),
    
    # Jenis Koperasi Management APIs
    path('api/jenis-koperasi/', views.jenis_koperasi_api, name='jenis_koperasi_api'),
    
    # Additional APIs
    path('categories/dropdown/', views.business_categories_dropdown, name='business_categories_dropdown'),
    path('dropdown/', views.businesses_dropdown, name='businesses_dropdown'),
    path('residents/dropdown/', views.residents_dropdown, name='residents_dropdown'),
    path('statistics/', views.business_statistics, name='business_statistics'),
    
    # Export APIs
    path('export/koperasi/', views.export_koperasi, name='export_koperasi'),
    path('export/bumg/', views.export_bumg, name='export_bumg'),
    path('export/ukm/', views.export_ukm, name='export_ukm'),
    path('export/aset/', views.export_aset, name='export_aset'),
    path('export/jasa/', views.export_jasa, name='export_jasa'),
    
    # Public API endpoints for statistics (no authentication required)
    path('public/koperasi/count/', views.koperasi_count_api, name='koperasi_count_api'),
    path('public/bumg/count/', views.bumg_count_api, name='bumg_count_api'),
    path('public/ukm/count/', views.ukm_count_api, name='ukm_count_api'),
    path('public/aset/count/', views.aset_count_api, name='aset_count_api'),
    path('public/jasa/count/', views.jasa_count_api, name='jasa_count_api'),
    path('public/statistics/', views.public_business_statistics, name='public_business_statistics'),
    
    # Detailed Statistics API endpoints
    path('api/koperasi/statistics/', views.koperasi_statistics_api, name='koperasi_statistics_api'),
    path('api/bumg/statistics/', views.bumg_statistics_api, name='bumg_statistics_api'),
    path('api/ukm/statistics/', views.ukm_statistics_api, name='ukm_statistics_api'),
    path('api/aset/statistics/', views.aset_statistics_api, name='aset_statistics_api'),
    path('api/layanan/statistics/', views.layanan_statistics_api, name='layanan_statistics_api'),
    path('api/kategori/statistics/', views.kategori_statistics_api, name='kategori_statistics_api'),
]