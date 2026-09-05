from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Documents module view
    path('', views.documents_admin, name='documents_admin'),
    
    # DocumentType APIs
    path('types/', views.document_type_list_api, name='documenttype_list'),
    path('types/<int:pk>/', views.document_type_detail_api, name='documenttype_detail'),
    path('types/create/', views.document_type_create_api, name='documenttype_create'),
    path('types/<int:pk>/update/', views.document_type_update_api, name='documenttype_update'),
    path('types/<int:pk>/delete/', views.document_type_delete_api, name='documenttype_delete'),
    
    # Document APIs
    path('documents/', views.document_list_api, name='document_list'),
    path('documents/<int:pk>/', views.document_detail_api, name='document_detail'),
    path('documents/create/', views.document_create_api, name='document_create'),
    path('documents/<int:pk>/update/', views.document_update_api, name='document_update'),
    path('documents/<int:pk>/delete/', views.document_delete_api, name='document_delete'),
    
    # DocumentRequest APIs
    path('requests/', views.document_request_list_api, name='documentrequest_list'),
    
    # DocumentTemplate APIs
    path('templates/', views.document_template_list_api, name='documenttemplate_list'),
    
    # Statistics API
    path('statistics/', views.documents_statistics_api, name='documents_statistics'),
    
    # Dropdown APIs
    path('types/dropdown/', views.document_types_dropdown_api, name='document_types_dropdown'),
    path('residents/dropdown/', views.residents_dropdown_api, name='residents_dropdown'),
    path('documents/dropdown/', views.documents_dropdown_api, name='documents_dropdown'),
]