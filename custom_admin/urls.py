from django.urls import path, include
from . import views

app_name = 'custom_admin'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),
    
    # Main dashboard
    path('', views.admin_dashboard, name='dashboard'),
    
    # API endpoints
    path('dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('recent-activities/', views.recent_activities_api, name='recent_activities_api'),
    path('system-info/', views.system_info_api, name='system_info_api'),
    path('search/', views.search_global, name='search_global'),
    
    # Module views
    path('module/<str:module_name>/', views.module_view, name='module_view'),
    
    # Profile and settings
    path('profile/', views.admin_profile, name='profile'),
    path('settings/', views.admin_settings, name='settings'),
    
    # Include API URLs from each app (references sudah di-include di main urls.py)
    path('core/', include('core.urls')),
    # path('references/', include('references.urls')),  # Commented out to avoid conflict
    path('village_profile/', include('village_profile.urls')),
    path('posyandu/', include('posyandu.urls')),
    # path('organization/', include('organization.urls')),  # Commented out to avoid double routing
    path('news/', include('news.urls')),
    path('letters/', include('letters.urls')),
    path('documents/', include('documents.urls')),
    path('business/', include('business.urls')),
    path('beneficiaries/', include('beneficiaries.urls')),
    path('organization/', include('organization.urls')),
]