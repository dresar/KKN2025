from django.urls import path
from . import views

app_name = 'posyandu'

urlpatterns = [
    # Main dashboard
    path('', views.posyandu_dashboard, name='posyandu_dashboard'),
    
    # Submenu Views
    path('pengaturan/', views.pengaturan_admin, name='pengaturan_admin'),
    path('kader/', views.kader_admin, name='kader_admin'),
    path('ibu-hamil/', views.ibu_hamil_admin, name='ibu_hamil_admin'),
    path('balita/', views.view_balita, name='view_balita'),
    path('lansia/', views.view_lansia, name='view_lansia'),
    path('stunting/', views.stunting_admin, name='stunting_admin'),
    path('penduduk/', views.penduduk_admin, name='penduduk_admin'),
    
    # Posyandu Location APIs
    path('api/locations/', views.posyandu_location_list, name='posyandu_location_list'),
    path('api/locations/<int:location_id>/', views.posyandu_location_detail, name='posyandu_location_detail'),
    path('api/locations/create/', views.posyandu_location_create, name='posyandu_location_create'),
    path('api/locations/<int:location_id>/update/', views.posyandu_location_update, name='posyandu_location_update'),
    path('api/locations/<int:location_id>/delete/', views.posyandu_location_delete, name='posyandu_location_delete'),
    
    # Posyandu Schedule APIs
    path('api/schedules/', views.posyandu_schedule_list, name='posyandu_schedule_list'),
    path('api/schedules/<int:schedule_id>/', views.posyandu_schedule_detail, name='posyandu_schedule_detail'),
    path('api/schedules/create/', views.posyandu_schedule_create, name='posyandu_schedule_create'),
    path('api/schedules/<int:schedule_id>/update/', views.posyandu_schedule_update, name='posyandu_schedule_update'),
    path('api/schedules/<int:schedule_id>/delete/', views.posyandu_schedule_delete, name='posyandu_schedule_delete'),
    
    # Posyandu Stats
    path('api/stats/', views.posyandu_stats, name='posyandu_stats'),
    
    # Helper APIs
    path('api/posyandu/list/', views.get_posyandu_locations, name='get_posyandu_list'),
    path('api/residents/list/', views.get_residents_for_posyandu, name='get_residents_list'),
    path('api/locations-dropdown/', views.get_posyandu_locations, name='get_posyandu_locations'),
    path('api/residents/', views.get_residents_for_posyandu, name='get_residents_for_posyandu'),
    path('api/ibu-hamil/dropdown/', views.get_ibu_hamil_dropdown, name='get_ibu_hamil_dropdown'),
    path('api/ibu-hamil/list/', views.get_ibu_hamil_dropdown, name='get_ibu_hamil_list'),
    path('api/children/list/', views.get_children_for_posyandu, name='get_children_list'),
    
    # Template compatibility URLs
    path('get-posyandu-locations/', views.get_posyandu_locations, name='get_posyandu_locations_compat'),
    path('get-residents-for-posyandu/', views.get_residents_for_posyandu, name='get_residents_for_posyandu_compat'),
    
    # Kader APIs
    path('api/kader/', views.kader_list_api, name='kader_list_api'),
    path('api/kader/<int:kader_id>/', views.kader_detail_api, name='kader_detail_api'),
    path('api/kader/create/', views.kader_create_api, name='kader_create_api'),
    path('api/kader/<int:kader_id>/update/', views.kader_update_api, name='kader_update_api'),
    path('api/kader/<int:kader_id>/delete/', views.kader_delete_api, name='kader_delete_api'),
    
    # Ibu Hamil APIs
    path('api/ibu-hamil/', views.ibu_hamil_list_api, name='ibu_hamil_list_api'),
    path('api/ibu-hamil/<int:ibu_id>/', views.ibu_hamil_detail_api, name='ibu_hamil_detail_api'),
    path('api/ibu-hamil/create/', views.ibu_hamil_create_api, name='ibu_hamil_create_api'),
    path('api/ibu-hamil/<int:ibu_id>/update/', views.ibu_hamil_update_api, name='ibu_hamil_update_api'),
    path('api/ibu-hamil/<int:ibu_id>/delete/', views.ibu_hamil_delete_api, name='ibu_hamil_delete_api'),
    
    # Pemeriksaan Ibu Hamil APIs
    path('api/pemeriksaan-ibu-hamil/', views.pemeriksaan_ibu_hamil_list_api, name='pemeriksaan_ibu_hamil_list_api'),
    path('api/pemeriksaan-ibu-hamil/create/', views.pemeriksaan_ibu_hamil_create_api, name='pemeriksaan_ibu_hamil_create_api'),
    path('api/pemeriksaan-ibu-hamil/<int:pemeriksaan_id>/update/', views.pemeriksaan_ibu_hamil_update_api, name='pemeriksaan_ibu_hamil_update_api'),
    path('api/pemeriksaan-ibu-hamil/<int:pemeriksaan_id>/delete/', views.pemeriksaan_ibu_hamil_delete_api, name='pemeriksaan_ibu_hamil_delete_api'),
    
    # Balita APIs (using existing nutrition data)
    path('api/balita/', views.balita_list_api, name='balita_list_api'),
    path('api/balita/<int:balita_id>/', views.balita_detail_api, name='balita_detail_api'),
    path('api/balita/create/', views.balita_create_api, name='balita_create_api'),
    path('api/balita/<int:balita_id>/update/', views.balita_update_api, name='balita_update_api'),
    path('api/balita/<int:balita_id>/delete/', views.balita_delete_api, name='balita_delete_api'),
    
    # Lansia APIs (using health records)
    path('api/lansia/', views.lansia_list_api, name='lansia_list_api'),
    path('api/lansia/<int:lansia_id>/', views.lansia_detail_api, name='lansia_detail_api'),
    path('api/lansia/create/', views.lansia_create_api, name='lansia_create_api'),
    path('api/lansia/<int:lansia_id>/update/', views.lansia_update_api, name='lansia_update_api'),
    path('api/lansia/<int:lansia_id>/delete/', views.lansia_delete_api, name='lansia_delete_api'),
    
    # Statistics APIs
    path('api/balita/stats/', views.balita_stats_api, name='balita_stats_api'),
    path('api/kader/stats/', views.kader_stats_api, name='kader_stats_api'),
    path('api/ibu-hamil/stats/', views.ibu_hamil_stats_api, name='ibu_hamil_stats_api'),
    path('api/stunting/stats/', views.stunting_stats_api, name='stunting_stats_api'),
    path('api/lansia/stats/', views.lansia_stats_api, name='lansia_stats_api'),
    
    # Stunting APIs
    path('api/stunting/', views.stunting_list_api, name='stunting_list_api'),
    path('api/stunting/<int:stunting_id>/', views.stunting_detail_api, name='stunting_detail_api'),
    path('api/stunting/create/', views.stunting_create_api, name='stunting_create_api'),
    path('api/stunting/<int:stunting_id>/update/', views.stunting_update_api, name='stunting_update_api'),
    path('api/stunting/<int:stunting_id>/delete/', views.stunting_delete_api, name='stunting_delete_api'),
    
    # Penduduk APIs
    path('api/penduduk/', views.penduduk_list_api, name='penduduk_list_api'),
    path('api/penduduk/<int:penduduk_id>/', views.penduduk_detail_api, name='penduduk_detail_api'),
    path('api/penduduk/create/', views.penduduk_create_api, name='penduduk_create_api'),
    path('api/penduduk/update/<int:penduduk_id>/', views.penduduk_update_api, name='penduduk_update_api'),
    path('api/penduduk/delete/<int:penduduk_id>/', views.penduduk_delete_api, name='penduduk_delete_api'),
    path('api/dusun/dropdown/', views.get_dusun_dropdown, name='get_dusun_dropdown'),
]