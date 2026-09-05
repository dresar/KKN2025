from django.urls import path
from . import api_views

app_name = 'core_api'

# Note: Most public APIs have been moved to public.api_urls
# This file now contains only admin/internal APIs if any
urlpatterns = [
    # Add admin-specific APIs here if needed
]