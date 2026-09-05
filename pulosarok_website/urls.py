"""
URL configuration for pulosarok_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),
    
    # Public pages and API (root level)
    path('', include('public.urls')),
    
    # Additional API endpoints (no authentication required)
    path('api/references/', include('references.urls')),
    
    # Custom admin interface
    path('pulosarok/', include('custom_admin.urls')),
    path('pulosarok/core/', include('core.urls')),
    path('pulosarok/references/', include('references.urls')),
    path('pulosarok/village-profile/', include('village_profile.urls')),
    path('pulosarok/organization/', include('organization.urls')),
    path('pulosarok/business/', include('business.urls')),
    path('pulosarok/posyandu/', include('posyandu.urls')),
    
    path('pulosarok/beneficiaries/', include('beneficiaries.urls')),
    path('pulosarok/api/beneficiaries/', include('beneficiaries.api_urls')),
    path('pulosarok/documents/', include('documents.urls')),
    path('pulosarok/news/', include('news.urls')),
    path('pulosarok/letters/', include('letters.urls')),
    path('pulosarok/tourism/', include('tourism.urls')),
    # Note: services app doesn't exist yet, but templates are ready
    # path('pulosarok/services/', include('services.urls')),
]

# Serve media files during development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)
