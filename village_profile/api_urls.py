from django.urls import path
from . import api_views, views

app_name = 'village_profile_api'

urlpatterns = [
    # Village Profile - only history data
    path('api/', api_views.api_village_profile, name='village_profile'),
    
    # History API - only module kept
    path('api/history/', api_views.api_village_history_list, name='history_list'),
    path('api/history/<int:history_id>/', api_views.api_village_history_detail, name='history_detail'),
    path('api/history/featured/', api_views.api_village_history_featured, name='history_featured'),
    path('api/history/stats/', api_views.api_village_history_stats, name='history_stats'),
    path('api/history/search/', api_views.api_village_history_search, name='history_search'),
    path('api/history/<int:history_id>/photos/', api_views.api_village_history_photos, name='history_photos'),
    
    # CRUD API endpoints for AJAX
    path('api/history/create/', api_views.api_village_history_create, name='history_create'),
    path('api/history/<int:history_id>/update/', api_views.api_village_history_update, name='history_update'),
    path('api/history/<int:history_id>/delete/', api_views.api_village_history_delete, name='history_delete'),
    path('api/history/<int:history_id>/photo-upload/', api_views.api_village_history_photo_upload, name='history_photo_upload'),
    path('api/history/photo/<int:photo_id>/delete/', api_views.api_village_history_photo_delete, name='history_photo_delete'),
    
    # Organization
    path('api/organization/stats/', api_views.api_organization_stats, name='organization_stats'),
]