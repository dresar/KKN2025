from django.contrib import admin
from .models import (
    DocumentType,
    Document,
    DocumentRequest,
    DocumentApproval,
    DocumentTemplate
)


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'processing_time_days', 'fee', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['document_number', 'title', 'document_type', 'applicant', 'status', 'priority', 'submission_date', 'completion_date']
    list_filter = ['status', 'priority', 'document_type', 'submission_date', 'completion_date']
    search_fields = ['document_number', 'title', 'applicant__nama', 'applicant__nik']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['applicant', 'created_by']
    date_hierarchy = 'submission_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informasi Dokumen', {
            'fields': ('document_type', 'applicant', 'document_number', 'title')
        }),
        ('Konten & Status', {
            'fields': ('content', 'status', 'priority')
        }),
        ('Tanggal & Waktu', {
            'fields': ('submission_date', 'completion_date')
        }),
        ('File & Catatan', {
            'fields': ('file_attachment', 'notes', 'created_by')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = ['requester', 'document_type', 'purpose', 'status', 'request_date', 'expected_completion_date', 'processed_by']
    list_filter = ['status', 'document_type', 'request_date', 'expected_completion_date']
    search_fields = ['requester__nama', 'requester__nik', 'document_type__name', 'purpose']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['requester', 'processed_by']
    date_hierarchy = 'request_date'
    ordering = ['-request_date']
    
    fieldsets = (
        ('Informasi Permintaan', {
            'fields': ('document_type', 'requester', 'purpose', 'status')
        }),
        ('Detail Permintaan', {
            'fields': ('additional_info', 'expected_completion_date', 'supporting_documents')
        }),
        ('Pemrosesan', {
            'fields': ('processed_by', 'processed_date', 'notes')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(DocumentApproval)
class DocumentApprovalAdmin(admin.ModelAdmin):
    list_display = ['document', 'approver', 'approval_level', 'status', 'approval_date', 'is_final_approval']
    list_filter = ['status', 'approval_level', 'is_final_approval', 'approval_date']
    search_fields = ['document__title', 'document__document_number', 'approver__username', 'approver__first_name', 'approver__last_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['document', 'approver']
    date_hierarchy = 'approval_date'
    ordering = ['approval_level', '-created_at']
    
    fieldsets = (
        ('Informasi Persetujuan', {
            'fields': ('document', 'approver', 'approval_level', 'status')
        }),
        ('Detail Persetujuan', {
            'fields': ('approval_date', 'comments', 'signature', 'is_final_approval')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'document_type', 'is_default', 'is_active', 'created_by', 'created_at']
    list_filter = ['template_type', 'document_type', 'is_default', 'is_active', 'created_at']
    search_fields = ['name', 'document_type__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['document_type', 'created_by']
    ordering = ['name']
    
    fieldsets = (
        ('Informasi Template', {
            'fields': ('name', 'template_type', 'document_type')
        }),
        ('Konten Template', {
            'fields': ('content_template', 'variables', 'header_template', 'footer_template')
        }),
        ('Pengaturan', {
            'fields': ('is_default', 'is_active', 'created_by')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
