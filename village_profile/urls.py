from django.urls import path, include
from django.views.generic import TemplateView
from . import views

app_name = 'village_profile'

urlpatterns = [
    # API endpoints
    path('', include('village_profile.api_urls')),
    # Dashboard URLs
    path('', views.village_profile_dashboard, name='dashboard'),
    
    # Overview page
    path('overview/', views.village_profile_overview, name='overview'),
    
    # Sejarah page
    path('sejarah/', views.sejarah_page, name='sejarah'),
    
    # History URLs
    path('history/', views.VillageHistoryListView.as_view(), name='history_list'),
    path('history/add/', views.VillageHistoryCreateView.as_view(), name='history_add'),
    path('history/<int:pk>/', views.VillageHistoryDetailView.as_view(), name='history_detail'),
    path('history/<int:pk>/edit/', views.VillageHistoryUpdateView.as_view(), name='history_edit'),
    path('history/<int:pk>/delete/', views.VillageHistoryDeleteView.as_view(), name='history_delete'),
    
    # Utility URLs
    path('stats/', views.village_profile_stats, name='stats'),
    path('history/search/', views.village_history_search, name='history_search'),
    path('history/export/', views.village_history_export, name='history_export'),
    
]