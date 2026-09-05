from django.contrib import admin
from .models import (
    BeneficiaryCategory,
    Beneficiary,
    Aid,
    AidDistribution,
    BeneficiaryVerification
)


@admin.register(BeneficiaryCategory)
class BeneficiaryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ['person', 'category', 'status', 'economic_status', 'registration_date', 'verification_date']
    list_filter = ['status', 'economic_status', 'category', 'registration_date', 'verification_date']
    search_fields = ['person__nama', 'person__nik', 'category__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['person', 'registered_by']
    date_hierarchy = 'registration_date'
    ordering = ['-registration_date']
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('person', 'category', 'registration_date', 'status')
        }),
        ('Status Ekonomi', {
            'fields': ('economic_status', 'monthly_income', 'family_members_count')
        }),
        ('Kondisi Rumah & Kebutuhan Khusus', {
            'fields': ('house_condition', 'special_needs')
        }),
        ('Verifikasi & Catatan', {
            'fields': ('verification_date', 'notes', 'registered_by')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Aid)
class AidAdmin(admin.ModelAdmin):
    list_display = ['name', 'aid_type', 'source', 'value_per_beneficiary', 'target_beneficiaries', 'start_date', 'end_date', 'is_active']
    list_filter = ['aid_type', 'source', 'is_active', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['created_by']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    
    fieldsets = (
        ('Informasi Bantuan', {
            'fields': ('name', 'aid_type', 'source', 'description')
        }),
        ('Anggaran & Target', {
            'fields': ('value_per_beneficiary', 'total_budget', 'target_beneficiaries')
        }),
        ('Periode & Persyaratan', {
            'fields': ('start_date', 'end_date', 'requirements')
        }),
        ('Status & Pembuat', {
            'fields': ('is_active', 'created_by')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(AidDistribution)
class AidDistributionAdmin(admin.ModelAdmin):
    list_display = ['beneficiary', 'aid', 'status', 'amount_received', 'distribution_date', 'receipt_number']
    list_filter = ['status', 'distribution_date', 'aid__aid_type', 'aid__source']
    search_fields = ['beneficiary__person__nama', 'aid__name', 'receipt_number']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['aid', 'beneficiary', 'distributed_by']
    date_hierarchy = 'distribution_date'
    ordering = ['-distribution_date']
    
    fieldsets = (
        ('Informasi Distribusi', {
            'fields': ('aid', 'beneficiary', 'distribution_date', 'status')
        }),
        ('Detail Penyaluran', {
            'fields': ('amount_received', 'receipt_number', 'distributed_by')
        }),
        ('Catatan', {
            'fields': ('notes',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(BeneficiaryVerification)
class BeneficiaryVerificationAdmin(admin.ModelAdmin):
    list_display = ['beneficiary', 'verification_date', 'verification_status', 'verifier', 'field_visit_conducted', 'next_verification_date']
    list_filter = ['verification_status', 'field_visit_conducted', 'verification_date', 'next_verification_date']
    search_fields = ['beneficiary__person__nama', 'verifier__username', 'verification_notes']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['beneficiary', 'verifier']
    date_hierarchy = 'verification_date'
    ordering = ['-verification_date']
    
    fieldsets = (
        ('Informasi Verifikasi', {
            'fields': ('beneficiary', 'verification_date', 'verification_status', 'verifier')
        }),
        ('Detail Verifikasi', {
            'fields': ('verification_notes', 'documents_checked')
        }),
        ('Kunjungan Lapangan', {
            'fields': ('field_visit_conducted', 'field_visit_notes')
        }),
        ('Tindak Lanjut', {
            'fields': ('next_verification_date',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
