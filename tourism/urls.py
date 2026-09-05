from django.urls import path, include
from . import views

app_name = 'tourism'

urlpatterns = [
    # API endpoints
    path('api/', include('tourism.api_urls')),
    
    # Public views
    path('', views.tourism_dashboard, name='dashboard'),
    path('locations/', views.tourism_list, name='location_list'),
    path('location/<slug:slug>/', views.tourism_detail, name='location_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('events/', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('packages/', views.package_list, name='package_list'),
    path('package/<int:package_id>/', views.package_detail, name='package_detail'),
    path('search/', views.search_tourism, name='search'),
    
    # User actions (require login)
    path('review/<int:location_id>/', views.submit_review, name='submit_review'),
    path('rating/<int:location_id>/', views.submit_rating, name='submit_rating'),
    
    # Admin views (require login)
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/locations/', views.admin_location_list, name='admin_location_list'),
    path('admin/location/create/', views.admin_location_create, name='admin_location_create'),
    path('admin/location/<int:location_id>/', views.admin_location_detail, name='admin_location_detail'),
    path('admin/location/<int:location_id>/edit/', views.admin_location_edit, name='admin_location_edit'),
    path('admin/location/<int:location_id>/delete/', views.admin_location_delete, name='admin_location_delete'),
    
    # Admin Category views
    path('admin/categories/', views.admin_category_list, name='admin_category_list'),
    path('admin/category/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/category/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/category/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    # Admin Package views
    path('admin/packages/', views.admin_package_list, name='admin_package_list'),
    path('admin/package/create/', views.admin_package_create, name='admin_package_create'),
    path('admin/package/<int:package_id>/', views.admin_package_detail, name='admin_package_detail'),
    path('admin/package/<int:package_id>/edit/', views.admin_package_edit, name='admin_package_edit'),
    path('admin/package/<int:package_id>/delete/', views.admin_package_delete, name='admin_package_delete'),
    
    # Admin Event views now handled by AJAX modals
]
