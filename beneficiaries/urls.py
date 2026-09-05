from django.urls import path
from . import views

app_name = 'beneficiaries'

urlpatterns = [
    # Beneficiaries module view
    path('', views.beneficiaries_list, name='beneficiaries_admin'),
    
    # BeneficiaryCategory APIs
    path('categories/', views.beneficiary_categories_list, name='beneficiarycategory_list'),
    path('categories/<int:pk>/', views.beneficiary_category_detail, name='beneficiarycategory_detail'),
    path('categories/create/', views.beneficiary_category_create, name='beneficiarycategory_create'),
    path('categories/<int:pk>/update/', views.beneficiary_category_update, name='beneficiarycategory_update'),
    path('categories/<int:pk>/delete/', views.beneficiary_category_delete, name='beneficiarycategory_delete'),
    
    # Beneficiary APIs
    path('beneficiaries/', views.beneficiaries_list, name='beneficiary_list'),
    path('beneficiaries/<int:pk>/', views.beneficiary_detail, name='beneficiary_detail'),
    path('beneficiaries/create/', views.beneficiary_create, name='beneficiary_create'),
    path('beneficiaries/<int:pk>/update/', views.beneficiary_update, name='beneficiary_update'),
    path('beneficiaries/<int:pk>/delete/', views.beneficiary_delete, name='beneficiary_delete'),
    
    # AidProgram APIs
    path('programs/', views.aids_list, name='aidprogram_list'),
    path('programs/<int:pk>/', views.aid_detail, name='aidprogram_detail'),
    path('programs/create/', views.aid_create, name='aidprogram_create'),
    path('programs/<int:pk>/update/', views.aid_update, name='aidprogram_update'),
    path('programs/<int:pk>/delete/', views.aid_delete, name='aidprogram_delete'),
    
    # AidDistribution APIs
    path('distributions/', views.aid_distributions_list, name='aiddistribution_list'),
    path('distributions/<int:pk>/', views.aid_distribution_detail, name='aiddistribution_detail'),
    path('distributions/create/', views.aid_distribution_create, name='aiddistribution_create'),
    path('distributions/<int:pk>/update/', views.aid_distribution_update, name='aiddistribution_update'),
    path('distributions/<int:pk>/delete/', views.aid_distribution_delete, name='aiddistribution_delete'),
    
    # BeneficiaryVerification APIs
    path('verifications/', views.beneficiary_verifications_list, name='beneficiaryverification_list'),
    path('verifications/<int:pk>/', views.beneficiary_verification_detail, name='beneficiaryverification_detail'),
    path('verifications/create/', views.beneficiary_verification_create, name='beneficiaryverification_create'),
    path('verifications/<int:pk>/update/', views.beneficiary_verification_update, name='beneficiaryverification_update'),
    path('verifications/<int:pk>/delete/', views.beneficiary_verification_delete, name='beneficiaryverification_delete'),
    
    # Additional APIs
    path('categories/dropdown/', views.beneficiary_categories_dropdown, name='beneficiary_categories_dropdown'),
    path('aids/dropdown/', views.aids_dropdown, name='aids_dropdown'),
    path('dropdown/', views.beneficiaries_dropdown, name='beneficiaries_dropdown'),
    path('residents/dropdown/', views.residents_dropdown, name='residents_dropdown'),
    path('statistics/', views.beneficiaries_statistics, name='beneficiaries_statistics'),
    
    # ============ NEW MODULE ROUTES ============
    
    # Dashboard and Module Pages
    path('dashboard/', views.beneficiaries_dashboard, name='beneficiaries_dashboard'),
    path('taraf-kehidupan/', views.taraf_kehidupan_page, name='taraf_kehidupan_page'),
    path('data-bantuan/', views.data_bantuan_page, name='data_bantuan_page'),
    path('data-bantuan/create/', views.create_bantuan_page, name='create_bantuan_page'),
    path('data-bantuan/<int:bantuan_id>/edit/', views.edit_bantuan_page, name='edit_bantuan_page'),
    path('upload-dokumen/', views.upload_dokumen_page, name='upload_dokumen_page'),
    path('membuat-berita/', views.membuat_berita_page, name='membuat_berita_page'),
    path('membuat-surat/', views.membuat_surat_page, name='membuat_surat_page'),
    
    # Taraf Kehidupan APIs
    path('api/taraf-kehidupan/', views.taraf_kehidupan_list, name='taraf_kehidupan_list'),
    path('api/taraf-kehidupan/create/', views.taraf_kehidupan_create, name='taraf_kehidupan_create'),
    path('api/taraf-kehidupan/<int:taraf_id>/', views.taraf_kehidupan_detail, name='taraf_kehidupan_detail'),
    path('api/taraf-kehidupan/<int:taraf_id>/update/', views.taraf_kehidupan_update, name='taraf_kehidupan_update'),
    path('api/taraf-kehidupan/<int:taraf_id>/delete/', views.taraf_kehidupan_delete, name='taraf_kehidupan_delete'),
    
    # Data Bantuan APIs
    path('api/data-bantuan/', views.data_bantuan_list, name='data_bantuan_list'),
    path('api/data-bantuan/create/', views.data_bantuan_create, name='data_bantuan_create'),
    path('api/data-bantuan/<int:bantuan_id>/', views.data_bantuan_detail, name='data_bantuan_detail'),
    path('api/data-bantuan/<int:bantuan_id>/update/', views.data_bantuan_update, name='data_bantuan_update'),
    path('api/data-bantuan/<int:bantuan_id>/delete/', views.data_bantuan_delete, name='data_bantuan_delete'),
    
    # Dokumen Gampong APIs
    path('api/dokumen-gampong/', views.dokumen_gampong_list, name='dokumen_gampong_list'),
    path('api/dokumen-gampong/create/', views.dokumen_gampong_create, name='dokumen_gampong_create'),
    path('api/dokumen-gampong/<int:dokumen_id>/', views.dokumen_gampong_detail, name='dokumen_gampong_detail'),
    path('api/dokumen-gampong/<int:dokumen_id>/update/', views.dokumen_gampong_update, name='dokumen_gampong_update'),
    path('api/dokumen-gampong/<int:dokumen_id>/delete/', views.dokumen_gampong_delete, name='dokumen_gampong_delete'),
    
    # Berita APIs
    path('api/berita/', views.berita_list, name='berita_list'),
    path('api/berita/create/', views.berita_create, name='berita_create'),
    path('api/berita/<int:berita_id>/', views.berita_detail, name='berita_detail'),
    path('api/berita/<int:berita_id>/update/', views.berita_update, name='berita_update'),
    path('api/berita/<int:berita_id>/delete/', views.berita_delete, name='berita_delete'),
    
    # Surat APIs
    path('api/surat/', views.surat_list, name='surat_list'),
    path('api/surat/create/', views.surat_create, name='surat_create'),
    path('api/surat/<int:surat_id>/', views.surat_detail, name='surat_detail'),
    path('api/surat/<int:surat_id>/update/', views.surat_update, name='surat_update'),
    path('api/surat/<int:surat_id>/delete/', views.surat_delete, name='surat_delete'),
    
    # Letter Template APIs
    path('api/letter-templates/', views.letter_template_list, name='letter_template_list'),
    
    # Export APIs
    path('export/taraf-kehidupan/csv/', views.export_taraf_kehidupan_csv, name='export_taraf_kehidupan_csv'),
    path('export/data-bantuan/csv/', views.export_data_bantuan_csv, name='export_data_bantuan_csv'),
    path('export/beneficiaries/csv/', views.export_beneficiaries_csv, name='export_beneficiaries_csv'),
    
    # Dashboard Statistics
    path('api/dashboard-statistics/', views.dashboard_statistics, name='dashboard_statistics'),
]