from django.urls import path
from . import api_views
from organization import api_views as org_api_views

app_name = 'public_api'

urlpatterns = [
    # Stats API
    path('stats/', api_views.api_stats, name='stats'),
    
    # News API
    path('news/', api_views.api_news, name='news'),
    
    # Events API
    path('events/', api_views.api_events, name='events'),
    path('events/<int:event_id>/', api_views.api_event_detail, name='event_detail'),
    
    # Village Profile API
    path('village-profile/', api_views.api_village_profile, name='village_profile'),
    
    # Village History API
    path('village-history/', api_views.api_village_history, name='village_history'),
    path('village-history/<int:history_id>/', api_views.api_village_history_detail, name='village_history_detail'),
    path('village-history/featured/', api_views.api_village_history_featured, name='village_history_featured'),
    
    # Population API (from references)
    path('references/population-api/', api_views.api_population, name='population'),
    path('references/dusun-api/', api_views.api_dusun, name='dusun'),
    
    # Organization API (Public)
    path('organization/stats/', org_api_views.api_organization_stats, name='organization_stats'),
    path('organization/perangkat-desa/', org_api_views.api_perangkat_desa, name='perangkat_desa'),
    path('organization/lembaga-adat/', org_api_views.api_lembaga_adat, name='lembaga_adat'),
    path('organization/penggerak-pkk/', org_api_views.api_penggerak_pkk, name='penggerak_pkk'),
    path('organization/kepemudaan/', org_api_views.api_kepemudaan, name='kepemudaan'),
    path('organization/karang-taruna/', org_api_views.api_karang_taruna, name='karang_taruna'),
    path('organization/structure/', org_api_views.api_organization_structure, name='organization_structure'),
    
    # Contact API
    path('contact/', api_views.api_contact, name='contact'),
    path('messages/', api_views.api_messages, name='messages'),
]