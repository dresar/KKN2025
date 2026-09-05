from django.contrib import admin
from .models import (BusinessCategory, Business, BusinessOwner, BusinessProduct, BusinessFinance,
                    Koperasi, BUMG, UKM, Aset, LayananJasa, JenisKoperasi)


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'business_type', 'status', 'employee_count', 'established_date')
    list_filter = ('category', 'business_type', 'status')
    search_fields = ('name', 'description', 'address')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'established_date'


@admin.register(BusinessOwner)
class BusinessOwnerAdmin(admin.ModelAdmin):
    list_display = ('owner', 'business', 'ownership_percentage', 'role', 'is_active')
    list_filter = ('is_active', 'business__business_type')
    search_fields = ('owner__nama', 'business__name', 'role')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('owner',)


@admin.register(BusinessProduct)
class BusinessProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'price', 'stock_quantity', 'is_available')
    list_filter = ('is_available', 'business__category')
    search_fields = ('name', 'description', 'business__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BusinessFinance)
class BusinessFinanceAdmin(admin.ModelAdmin):
    list_display = ('business', 'transaction_type', 'amount', 'transaction_date', 'category')
    list_filter = ('transaction_type', 'business__business_type')
    search_fields = ('business__name', 'description', 'category')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'transaction_date'


@admin.register(JenisKoperasi)
class JenisKoperasiAdmin(admin.ModelAdmin):
    list_display = ('nama', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('nama', 'deskripsi')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Koperasi)
class KoperasiAdmin(admin.ModelAdmin):
    list_display = ('nama', 'nomor_badan_hukum', 'ketua', 'jumlah_anggota', 'status', 'created_at')
    list_filter = ('status', 'jenis_koperasi', 'created_at')
    search_fields = ('nama', 'ketua', 'nomor_badan_hukum', 'alamat')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'tanggal_berdiri'


@admin.register(BUMG)
class BUMGAdmin(admin.ModelAdmin):
    list_display = ('nama', 'nomor_sk', 'direktur', 'modal_dasar', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('nama', 'direktur', 'nomor_sk', 'alamat')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'tanggal_sk'


@admin.register(UKM)
class UKMAdmin(admin.ModelAdmin):
    list_display = ['nama_usaha', 'pemilik', 'jenis_usaha', 'skala_usaha', 'modal_awal', 'omzet_bulanan', 'status', 'created_at']
    list_filter = ['skala_usaha', 'status', 'jenis_usaha', 'created_at']
    search_fields = ['nama_usaha', 'pemilik', 'nik_pemilik', 'jenis_usaha']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'tanggal_mulai'


@admin.register(Aset)
class AsetAdmin(admin.ModelAdmin):
    list_display = ['nama_aset', 'kategori', 'kode_aset', 'lokasi', 'nilai_perolehan', 'kondisi', 'penanggung_jawab', 'created_at']
    list_filter = ['kategori', 'kondisi', 'tanggal_perolehan', 'created_at']
    search_fields = ['nama_aset', 'kode_aset', 'lokasi', 'penanggung_jawab']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'tanggal_perolehan'


@admin.register(LayananJasa)
class LayananJasaAdmin(admin.ModelAdmin):
    list_display = ['nama', 'kategori', 'penyedia', 'harga_min', 'harga_max', 'status', 'rating', 'created_at']
    list_filter = ['kategori', 'status', 'satuan_harga', 'created_at']
    search_fields = ['nama', 'penyedia', 'deskripsi', 'area_layanan']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
