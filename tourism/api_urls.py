from django.urls import path
from . import api_views

app_name = 'tourism_api'

urlpatterns = [
    # CSRF Token
    path('csrf-token/', api_views.api_csrf_token, name='csrf_token'),
    
    # Statistics
    path('stats/', api_views.api_stats, name='stats'),
    
    # Destinations (Public API)
    path('destinations/', api_views.api_destinations, name='destinations'),
    path('destinations/<int:destination_id>/', api_views.api_destination_detail, name='destination_detail'),
    path('destinations/<int:destination_id>/visit/', api_views.api_destination_visit, name='destination_visit'),
    
    # Gallery (Public API)
    path('gallery/', api_views.api_gallery, name='gallery'),
    
    # ==================== ADMIN CRUD API ENDPOINTS ====================
    
    # Tourism Locations CRUD
    path('admin/locations/', api_views.TourismLocationAPIView.as_view(), name='admin_locations'),
    path('admin/locations/<int:location_id>/', api_views.TourismLocationAPIView.as_view(), name='admin_location_detail'),
    
    # Tourism Categories CRUD
    path('admin/categories/', api_views.TourismCategoryAPIView.as_view(), name='admin_categories'),
    path('admin/categories/<int:category_id>/', api_views.TourismCategoryAPIView.as_view(), name='admin_category_detail'),
    
    # Tourism Events CRUD
    path('event/<int:event_id>/', api_views.TourismEventAPIView.as_view(), name='event_detail'),
    path('event/create/', api_views.TourismEventAPIView.as_view(), name='event_create'),
    path('event/<int:event_id>/update/', api_views.TourismEventAPIView.as_view(), name='event_update'),
    path('event/<int:event_id>/delete/', api_views.TourismEventAPIView.as_view(), name='event_delete'),
    
    # Tourism Reviews CRUD
    path('api/admin/reviews/', api_views.TourismReviewAPIView.as_view(), name='admin_reviews'),
    path('api/admin/reviews/<int:review_id>/', api_views.TourismReviewAPIView.as_view(), name='admin_review_detail'),
    
    # Tourism Packages CRUD
    path('api/admin/packages/', api_views.TourismPackageAPIView.as_view(), name='admin_packages'),
    path('api/admin/packages/<int:package_id>/', api_views.TourismPackageAPIView.as_view(), name='admin_package_detail'),
    
    # Tourism Gallery CRUD
    path('api/admin/gallery/', api_views.TourismGalleryAPIView.as_view(), name='admin_gallery'),
    path('api/admin/gallery/<int:gallery_id>/', api_views.TourismGalleryAPIView.as_view(), name='admin_gallery_detail'),
]