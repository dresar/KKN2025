from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Dusun, Lorong, Penduduk, DisabilitasType, DisabilitasData, ReligionReference

# Try to import Family model
try:
    from .models import Family
    FAMILY_MODEL_EXISTS = True
except ImportError:
    FAMILY_MODEL_EXISTS = False


@admin.register(Dusun)
class DusunAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'area_size', 'population_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Lorong)
class LorongAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'dusun', 'length', 'house_count', 'is_active')
    list_filter = ('dusun', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'dusun__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Penduduk)
class PendudukAdmin(admin.ModelAdmin):
    list_display = ('name', 'nik', 'gender', 'birth_date', 'age', 'dusun', 'is_active')
    list_filter = ('gender', 'marital_status', 'religion', 'dusun', 'is_active', 'created_at')
    search_fields = ('name', 'nik', 'address')
    readonly_fields = ('created_at', 'updated_at', 'age')
    date_hierarchy = 'birth_date'

    def age(self, obj):
        return obj.age
    age.short_description = 'Umur'


@admin.register(DisabilitasType)
class DisabilitasTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DisabilitasData)
class DisabilitasDataAdmin(admin.ModelAdmin):
    list_display = ('penduduk', 'disability_type', 'severity', 'needs_assistance', 'is_active')
    list_filter = ('disability_type', 'severity', 'needs_assistance', 'is_active', 'created_at')
    search_fields = ('penduduk__name', 'penduduk__nik', 'disability_type__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ReligionReference)
class ReligionReferenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')


if FAMILY_MODEL_EXISTS:
    @admin.register(Family)
    class FamilyAdmin(admin.ModelAdmin):
        list_display = ('kk_number', 'head', 'family_status', 'total_members', 'dusun', 'is_active')
        list_filter = ('family_status', 'dusun', 'is_active', 'created_at')
        search_fields = ('kk_number', 'head__name', 'head__nik')
        readonly_fields = ('created_at', 'updated_at', 'full_address')
        list_per_page = 25
        
        fieldsets = (
            ('Informasi Kartu Keluarga', {
                'fields': ('kk_number', 'head', 'family_status', 'total_members', 'total_income')
            }),
            ('Alamat Keluarga', {
                'fields': ('dusun', 'lorong', 'rt_number', 'rw_number', 'house_number', 'address', 'postal_code')
            }),
            ('Kontak', {
                'fields': ('phone_number',)
            }),
            ('Status', {
                'fields': ('is_active',)
            }),
            ('Sistem', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )
        
        def full_address(self, obj):
            return obj.full_address
        full_address.short_description = 'Alamat Lengkap'
