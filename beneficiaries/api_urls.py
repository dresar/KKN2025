from django.urls import path
from . import api_views

app_name = 'beneficiaries_api'

urlpatterns = [
    # BeneficiaryCategory APIs
    path('categories/', api_views.beneficiary_categories_list, name='beneficiarycategory_list'),
    path('categories/<int:category_id>/', api_views.beneficiary_category_detail, name='beneficiarycategory_detail'),
    path('categories/create/', api_views.beneficiary_category_create, name='beneficiarycategory_create'),
    path('categories/<int:category_id>/update/', api_views.beneficiary_category_update, name='beneficiarycategory_update'),
    path('categories/<int:category_id>/delete/', api_views.beneficiary_category_delete, name='beneficiarycategory_delete'),
    
    # Beneficiary APIs
    path('beneficiaries/', api_views.beneficiaries_list, name='beneficiary_list'),
    path('beneficiaries/<int:beneficiary_id>/', api_views.beneficiary_detail, name='beneficiary_detail'),
    path('beneficiaries/create/', api_views.beneficiary_create, name='beneficiary_create'),
    path('beneficiaries/<int:beneficiary_id>/update/', api_views.beneficiary_update, name='beneficiary_update'),
    path('beneficiaries/<int:beneficiary_id>/delete/', api_views.beneficiary_delete, name='beneficiary_delete'),
    
    # Aid APIs
    path('aids/', api_views.aids_list, name='aid_list'),
    path('aids/<int:aid_id>/', api_views.aid_detail, name='aid_detail'),
    path('aids/create/', api_views.aid_create, name='aid_create'),
    path('aids/<int:aid_id>/update/', api_views.aid_update, name='aid_update'),
    path('aids/<int:aid_id>/delete/', api_views.aid_delete, name='aid_delete'),
    
    # AidDistribution APIs
    path('distributions/', api_views.aid_distributions_list, name='aiddistribution_list'),
    path('distributions/<int:distribution_id>/', api_views.aid_distribution_detail, name='aiddistribution_detail'),
    path('distributions/create/', api_views.aid_distribution_create, name='aiddistribution_create'),
    path('distributions/<int:distribution_id>/update/', api_views.aid_distribution_update, name='aiddistribution_update'),
    path('distributions/<int:distribution_id>/delete/', api_views.aid_distribution_delete, name='aiddistribution_delete'),
    
    # BeneficiaryVerification APIs
    path('verifications/', api_views.beneficiary_verifications_list, name='beneficiaryverification_list'),
    path('verifications/<int:verification_id>/', api_views.beneficiary_verification_detail, name='beneficiaryverification_detail'),
    path('verifications/create/', api_views.beneficiary_verification_create, name='beneficiaryverification_create'),
    path('verifications/<int:verification_id>/update/', api_views.beneficiary_verification_update, name='beneficiaryverification_update'),
    path('verifications/<int:verification_id>/delete/', api_views.beneficiary_verification_delete, name='beneficiaryverification_delete'),
    
    # TarafKehidupan APIs
    path('taraf-kehidupan/', api_views.taraf_kehidupan_list, name='taraf_kehidupan_list'),
    path('taraf-kehidupan/<int:taraf_id>/', api_views.taraf_kehidupan_detail, name='taraf_kehidupan_detail'),
    path('taraf-kehidupan/create/', api_views.taraf_kehidupan_create, name='taraf_kehidupan_create'),
    path('taraf-kehidupan/<int:taraf_id>/update/', api_views.taraf_kehidupan_update, name='taraf_kehidupan_update'),
    path('taraf-kehidupan/<int:taraf_id>/delete/', api_views.taraf_kehidupan_delete, name='taraf_kehidupan_delete'),
    
    # DataBantuan APIs
    path('data-bantuan/', api_views.data_bantuan_list, name='data_bantuan_list'),
    path('data-bantuan/<int:bantuan_id>/', api_views.data_bantuan_detail, name='data_bantuan_detail'),
    path('data-bantuan/create/', api_views.data_bantuan_create, name='data_bantuan_create'),
    path('data-bantuan/<int:bantuan_id>/update/', api_views.data_bantuan_update, name='data_bantuan_update'),
    path('data-bantuan/<int:bantuan_id>/delete/', api_views.data_bantuan_delete, name='data_bantuan_delete'),
    
    # Additional APIs
    path('statistics/', api_views.beneficiary_statistics, name='beneficiaries_statistics'),
    path('categories/dropdown/', api_views.beneficiary_categories_dropdown, name='beneficiary_categories_dropdown'),
    path('beneficiaries/dropdown/', api_views.beneficiaries_dropdown, name='beneficiaries_dropdown'),
    path('residents/dropdown/', api_views.penduduk_dropdown, name='residents_dropdown'),
    
    # Statistics APIs
    path('stats/by-category/', api_views.beneficiary_stats_by_category, name='beneficiary_stats_by_category'),
    path('stats/by-economic-status/', api_views.beneficiary_stats_by_economic_status, name='beneficiary_stats_by_economic_status'),
]