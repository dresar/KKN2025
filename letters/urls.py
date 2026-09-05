from django.urls import path, include
from . import views

app_name = 'letters'

urlpatterns = [
    # API endpoints
    path('', include('letters.api_urls')),
    # Admin views
    path('', views.letters_admin, name='admin'),
    path('dashboard/', views.letter_dashboard, name='dashboard'),
    path('', views.letter_list, name='list'),
    path('create/', views.letter_create, name='create'),
    path('<int:letter_id>/', views.letter_detail, name='detail'),
    path('<int:letter_id>/edit/', views.letter_edit, name='edit'),
    path('<int:letter_id>/delete/', views.letter_delete, name='delete'),
    
    # Export views
    path('<int:letter_id>/export/pdf/', views.letter_export_pdf, name='export_pdf'),
    path('<int:letter_id>/export/docx/', views.letter_export_docx, name='export_docx'),
    
    # Settings
    path('settings/', views.letter_settings, name='settings'),
    
    # Letter Type API
    path('letter-types/', views.letter_type_list_api, name='letter_type_list_api'),
    path('letter-types/create/', views.letter_type_create_api, name='letter_type_create_api'),
    path('letter-types/<int:pk>/', views.letter_type_detail_api, name='letter_type_detail_api'),
    path('letter-types/<int:pk>/update/', views.letter_type_update_api, name='letter_type_update_api'),
    path('letter-types/<int:pk>/delete/', views.letter_type_delete_api, name='letter_type_delete_api'),
    
    # Letter API
    path('letters/', views.letter_list_api, name='letter_list_api'),
    path('letters/create/', views.letter_create_api, name='letter_create_api'),
    path('letters/<int:pk>/', views.letter_detail_api, name='letter_detail_api'),
    path('letters/<int:pk>/update/', views.letter_update_api, name='letter_update_api'),
    path('letters/<int:pk>/delete/', views.letter_delete_api, name='letter_delete_api'),
    
    # AI Integration APIs
    path('letters/<int:pk>/ai/validate/', views.letter_ai_validate_api, name='letter_ai_validate_api'),
    path('letters/<int:pk>/ai/improve/', views.letter_ai_improve_api, name='letter_ai_improve_api'),
    path('letters/<int:pk>/ai/summarize/', views.letter_ai_summarize_api, name='letter_ai_summarize_api'),
    path('letters/ai/generate/', views.letter_ai_generate_api, name='letter_ai_generate_api'),
    
    # Digital Signature APIs
    path('letters/<int:pk>/signature/sign/', views.letter_digital_sign_api, name='letter_digital_sign_api'),
    path('letters/<int:pk>/signature/verify/', views.letter_signature_verify_api, name='letter_signature_verify_api'),
    
    # Template Management APIs
    path('templates/', views.letter_templates_api, name='letter_templates_api'),
    path('letters/<int:pk>/template/apply/', views.letter_apply_template_api, name='letter_apply_template_api'),
    
    # Letter Recipient API
    path('letters/<int:letter_id>/recipients/', views.letter_recipient_list_api, name='letter_recipient_list_api'),
    path('letters/<int:letter_id>/recipients/create/', views.letter_recipient_create_api, name='letter_recipient_create_api'),
    path('recipients/<int:pk>/', views.letter_recipient_detail_api, name='letter_recipient_detail_api'),
    path('recipients/<int:pk>/update/', views.letter_recipient_update_api, name='letter_recipient_update_api'),
    path('recipients/<int:pk>/delete/', views.letter_recipient_delete_api, name='letter_recipient_delete_api'),
    
    # Letter Attachment API
    path('letters/<int:letter_id>/attachments/', views.letter_attachment_list_api, name='letter_attachment_list_api'),
    path('letters/<int:letter_id>/attachments/create/', views.letter_attachment_create_api, name='letter_attachment_create_api'),
    path('attachments/<int:pk>/', views.letter_attachment_detail_api, name='letter_attachment_detail_api'),
    path('attachments/<int:pk>/update/', views.letter_attachment_update_api, name='letter_attachment_update_api'),
    path('attachments/<int:pk>/delete/', views.letter_attachment_delete_api, name='letter_attachment_delete_api'),
    
    # Letter Tracking API
    path('letters/<int:letter_id>/tracking/', views.letter_tracking_list_api, name='letter_tracking_list_api'),
    path('letters/<int:letter_id>/tracking/create/', views.letter_tracking_create_api, name='letter_tracking_create_api'),
    path('tracking/<int:pk>/', views.letter_tracking_detail_api, name='letter_tracking_detail_api'),
    path('tracking/<int:pk>/update/', views.letter_tracking_update_api, name='letter_tracking_update_api'),
    path('tracking/<int:pk>/delete/', views.letter_tracking_delete_api, name='letter_tracking_delete_api'),
]