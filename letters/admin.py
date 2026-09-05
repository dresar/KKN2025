from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    LetterType, Letter, LetterTracking, APIKeySettings, 
    LetterSettings, LetterTemplate, LetterAIValidation, 
    LetterDigitalSignature
)
from .services import GeminiAIService, LetterValidationService

@admin.register(LetterType)
class LetterTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description', 'letter_count', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['created_at']
    ordering = ['name']
    
    def letter_count(self, obj):
        count = obj.letter_set.count()
        return format_html(
            '<span class="badge badge-info">{}</span>',
            count
        )
    letter_count.short_description = 'Jumlah Surat'

@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = [
        'subject', 'letter_type', 'status_badge', 'letter_number', 
        'ai_status', 'signature_status', 'word_count', 'created_at'
    ]
    list_filter = [
        'status', 'letter_type', 'requires_ai_validation', 
        'is_digitally_signed', 'language', 'created_at'
    ]
    search_fields = ['subject', 'letter_number', 'content', 'public_url']
    readonly_fields = [
        'letter_number', 'created_at', 'updated_at', 'word_count',
        'estimated_reading_time', 'public_url', 'signature_hash'
    ]
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('subject', 'letter_type', 'content', 'language')
        }),
        ('Template & AI', {
            'fields': (
                'template', 'ai_generated_content', 'ai_suggestions_applied',
                'requires_ai_validation'
            ),
            'classes': ('collapse',)
        }),
        ('Status & Nomor', {
            'fields': ('status', 'letter_number')
        }),
        ('Digital Signature', {
            'fields': (
                'requires_digital_signature', 'is_digitally_signed', 
                'signature_hash'
            ),
            'classes': ('collapse',)
        }),
        ('Files & Export', {
            'fields': ('pdf_file', 'qr_code', 'public_url'),
            'classes': ('collapse',)
        }),
        ('Statistik', {
            'fields': ('word_count', 'estimated_reading_time'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['validate_with_ai', 'generate_pdf', 'mark_for_signature']
    
    def status_badge(self, obj):
        colors = {
            'draft': 'secondary',
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'sent': 'info',
            'archived': 'dark'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def ai_status(self, obj):
        if not obj.requires_ai_validation:
            return format_html('<span class="text-muted">-</span>')
        
        try:
            validation = obj.ai_validation
            if validation.status == 'valid':
                return format_html(
                    '<span class="badge badge-success">Valid ({:.1f})</span>',
                    validation.confidence_score
                )
            elif validation.status == 'invalid':
                return format_html(
                    '<span class="badge badge-danger">Invalid ({:.1f})</span>',
                    validation.confidence_score
                )
            else:
                return format_html(
                    '<span class="badge badge-warning">{}</span>',
                    validation.status.title()
                )
        except:
            return format_html('<span class="badge badge-secondary">Belum Divalidasi</span>')
    ai_status.short_description = 'AI Validation'
    
    def signature_status(self, obj):
        if not obj.requires_digital_signature:
            return format_html('<span class="text-muted">-</span>')
        
        if obj.is_digitally_signed:
            return format_html('<span class="badge badge-success">Signed</span>')
        else:
            return format_html('<span class="badge badge-warning">Pending</span>')
    signature_status.short_description = 'Digital Signature'
    
    def validate_with_ai(self, request, queryset):
        validation_service = LetterValidationService()
        validated_count = 0
        
        for letter in queryset:
            if letter.requires_ai_validation:
                validation_service.validate_letter(letter)
                validated_count += 1
        
        self.message_user(
            request,
            f'{validated_count} surat berhasil divalidasi dengan AI.'
        )
    validate_with_ai.short_description = 'Validasi dengan AI'
    
    def generate_pdf(self, request, queryset):
        generated_count = 0
        
        for letter in queryset:
            if letter.generate_pdf():
                generated_count += 1
        
        self.message_user(
            request,
            f'{generated_count} PDF berhasil dibuat.'
        )
    generate_pdf.short_description = 'Generate PDF'
    
    def mark_for_signature(self, request, queryset):
        updated = queryset.update(requires_digital_signature=True)
        self.message_user(
            request,
            f'{updated} surat ditandai untuk tanda tangan digital.'
        )
    mark_for_signature.short_description = 'Tandai untuk Tanda Tangan'

@admin.register(LetterTracking)
class LetterTrackingAdmin(admin.ModelAdmin):
    list_display = ['letter', 'action', 'performed_by', 'performed_at']
    list_filter = ['action', 'performed_at']
    search_fields = ['letter__subject', 'notes']
    readonly_fields = ['performed_at']
    
    def has_add_permission(self, request):
        return False  # Tracking entries are created automatically

@admin.register(APIKeySettings)
class APIKeySettingsAdmin(admin.ModelAdmin):
    list_display = [
        'service_name', 'is_active', 'current_usage', 
        'max_requests_per_day', 'created_at'
    ]
    list_filter = ['service_name', 'is_active', 'created_at']
    search_fields = ['service_name']
    readonly_fields = ['current_usage', 'last_reset_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Service Information', {
            'fields': ('service_name', 'is_active')
        }),
        ('API Key', {
            'fields': ('api_key',),
            'description': 'API key will be encrypted when saved.'
        }),
        ('Usage Statistics', {
            'fields': ('current_usage', 'max_requests_per_day', 'last_reset_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.extend(['service_name'])
        return readonly

@admin.register(LetterSettings)
class LetterSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'village_name', 'is_active', 'letter_number_format', 
        'enable_ai_validation', 'created_at'
    ]
    list_filter = ['is_active', 'enable_ai_validation', 'enable_digital_signature']
    search_fields = ['village_name', 'village_address']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Village Information', {
            'fields': (
                'village_name', 'village_address', 'village_code',
                'head_of_village_name', 'secretary_name'
            )
        }),
        ('Letter Configuration', {
            'fields': (
                'letter_number_format', 'letterhead_image',
                'head_signature', 'secretary_signature'
            )
        }),
        ('AI & Digital Features', {
            'fields': (
                'ai_validation_enabled', 'ai_auto_suggestions',
                'digital_signature_enabled', 'require_approval_for_ai'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        # Ensure only one active settings
        if obj.is_active:
            LetterSettings.objects.filter(is_active=True).update(is_active=False)
        super().save_model(request, obj, form, change)

@admin.register(LetterTemplate)
class LetterTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'template_type', 'is_active', 'usage_count', 
        'created_by', 'created_at'
    ]
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'content_template']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'template_type', 'is_active')
        }),
        ('Content', {
            'fields': ('content_template', 'variables', 'css_styles')
        }),
        ('Metadata', {
            'fields': ('created_by', 'usage_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new template
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(LetterAIValidation)
class LetterAIValidationAdmin(admin.ModelAdmin):
    list_display = [
        'letter', 'status_badge', 'confidence_score', 
        'processing_time_ms', 'validated_at'
    ]
    list_filter = ['status', 'validated_at']
    search_fields = ['letter__subject', 'letter__letter_number']
    readonly_fields = [
        'validated_at', 'processing_time_ms', 'validation_id'
    ]
    
    fieldsets = (
        ('Validation Info', {
            'fields': ('letter', 'status', 'confidence_score')
        }),
        ('Results', {
            'fields': ('validation_result', 'suggestions', 'grammar_check', 'content_analysis')
        }),
        ('Performance', {
            'fields': ('processing_time_ms', 'validated_at'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        colors = {
            'valid': 'success',
            'invalid': 'danger',
            'pending': 'warning',
            'error': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.status.title()
        )
    status_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False  # Validations are created automatically

@admin.register(LetterDigitalSignature)
class LetterDigitalSignatureAdmin(admin.ModelAdmin):
    list_display = [
        'letter', 'signer', 'status_badge', 
        'signature_timestamp', 'is_valid'
    ]
    list_filter = ['status', 'signature_timestamp']
    search_fields = ['letter__subject', 'signer__username']
    readonly_fields = [
        'signature_hash', 'signature_timestamp', 'signature_data'
    ]
    
    fieldsets = (
        ('Signature Info', {
            'fields': ('letter', 'signer', 'status')
        }),
        ('Signature Data', {
            'fields': (
                'signature_hash', 'signature_data', 
                'certificate_info', 'signature_timestamp'
            ),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        colors = {
            'signed': 'success',
            'pending': 'warning',
            'invalid': 'danger',
            'revoked': 'dark'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.status.title()
        )
    status_badge.short_description = 'Status'
    
    def is_valid(self, obj):
        try:
            valid = obj.verify_signature()
            if valid:
                return format_html('<span class="badge badge-success">Valid</span>')
            else:
                return format_html('<span class="badge badge-danger">Invalid</span>')
        except:
            return format_html('<span class="badge badge-warning">Unknown</span>')
    is_valid.short_description = 'Signature Valid'
    
    def has_add_permission(self, request):
        return False  # Signatures are created through the signing process
