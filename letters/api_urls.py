from django.urls import path
from . import api_views

app_name = 'letters_api'

urlpatterns = [
    # Letter Types
    path('api/jenis-surat/', api_views.api_letter_types, name='letter_types'),
    
    # Letter Statistics
    path('api/stats/', api_views.api_letters_stats, name='letters_stats'),
    
    # Letter Creation
    path('api/', api_views.api_letters_create, name='letters_create'),
    
    # Letter Tracking
    path('api/track/<str:tracking_code>/', api_views.api_letters_track, name='letters_track'),
]