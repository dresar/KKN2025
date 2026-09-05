from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import VillageHistory, VillageHistoryPhoto, VillageHistoryPhoto


class VillageHistoryPhotoInline(admin.TabularInline):
    """Inline admin for VillageHistoryPhoto"""
    model = VillageHistoryPhoto
    extra = 1
    fields = ['image', 'caption', 'description', 'photographer', 'photo_date', 'location', 'is_featured', 'is_active', 'display_order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 60px; object-fit: cover; border-radius: 4px;"/>',
                obj.image.url
            )
        return "Belum ada gambar"
    image_preview.short_description = "Preview"


@admin.register(VillageHistory)
class VillageHistoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'history_type', 'period_display', 'photo_count_display', 'view_count', 'is_featured', 'is_active', 'featured_image_preview']
    list_filter = ['history_type', 'is_featured', 'is_active', 'year_start', 'created_at']
    search_fields = ['title', 'summary', 'content', 'author', 'source']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-is_featured', 'year_start', 'period_start']
    inlines = [VillageHistoryPhotoInline]
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('title', 'slug', 'history_type', 'summary')
        }),
        ('Konten', {
            'fields': ('content',)
        }),
        ('Periode Sejarah', {
            'fields': ('period_start', 'period_end', 'year_start', 'year_end'),
            'description': 'Isi periode dalam format teks atau tahun numerik'
        }),
        ('Gambar Utama', {
            'fields': ('featured_image', 'featured_image_caption'),
            'classes': ('collapse',)
        }),
        ('Informasi Tambahan', {
            'fields': ('author', 'source'),
            'classes': ('collapse',)
        }),
        ('Status & Metadata', {
            'fields': ('is_featured', 'is_active', 'view_count')
        })
    )
    
    readonly_fields = ['view_count']
    
    def period_display(self, obj):
        return obj.period_display
    period_display.short_description = "Periode"
    
    def photo_count_display(self, obj):
        count = obj.photo_count
        if count > 0:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{} foto</span>',
                count
            )
        return format_html('<span style="color: #6c757d;">Belum ada foto</span>')
    photo_count_display.short_description = "Jumlah Foto"
    
    def featured_image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 45px; object-fit: cover; border-radius: 4px;"/>',
                obj.featured_image.url
            )
        return "Tidak ada gambar"
    featured_image_preview.short_description = "Preview Gambar"
    
    actions = ['mark_as_featured', 'unmark_as_featured', 'activate_history', 'deactivate_history']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} sejarah berhasil ditandai sebagai unggulan.")
    mark_as_featured.short_description = "Tandai sebagai sejarah unggulan"
    
    def unmark_as_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"{queryset.count()} sejarah berhasil dihapus dari unggulan.")
    unmark_as_featured.short_description = "Hapus dari sejarah unggulan"
    
    def activate_history(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} sejarah berhasil diaktifkan.")
    activate_history.short_description = "Aktifkan sejarah terpilih"
    
    def deactivate_history(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} sejarah berhasil dinonaktifkan.")
    deactivate_history.short_description = "Nonaktifkan sejarah terpilih"


@admin.register(VillageHistoryPhoto)
class VillageHistoryPhotoAdmin(admin.ModelAdmin):
    list_display = ['history_title', 'caption', 'photographer', 'photo_date', 'location', 'is_featured', 'is_active', 'image_preview']
    list_filter = ['is_featured', 'is_active', 'photo_date', 'history__history_type']
    search_fields = ['caption', 'description', 'photographer', 'location', 'history__title']
    date_hierarchy = 'photo_date'
    ordering = ['history', 'display_order', '-is_featured']
    
    fieldsets = (
        ('Foto', {
            'fields': ('history', 'image')
        }),
        ('Informasi Foto', {
            'fields': ('caption', 'description')
        }),
        ('Metadata Foto', {
            'fields': ('photographer', 'photo_date', 'location'),
            'classes': ('collapse',)
        }),
        ('Pengaturan Tampilan', {
            'fields': ('is_featured', 'is_active', 'display_order')
        })
    )
    
    def history_title(self, obj):
        return obj.history.title
    history_title.short_description = "Sejarah"
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 60px; object-fit: cover; border-radius: 4px;"/>',
                obj.image.url
            )
        return "Tidak ada gambar"
    image_preview.short_description = "Preview"
    
    actions = ['mark_as_featured_photo', 'unmark_as_featured_photo', 'activate_photos', 'deactivate_photos']
    
    def mark_as_featured_photo(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} foto berhasil ditandai sebagai unggulan.")
    mark_as_featured_photo.short_description = "Tandai sebagai foto unggulan"
    
    def unmark_as_featured_photo(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"{queryset.count()} foto berhasil dihapus dari unggulan.")
    unmark_as_featured_photo.short_description = "Hapus dari foto unggulan"
    
    def activate_photos(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} foto berhasil diaktifkan.")
    activate_photos.short_description = "Aktifkan foto terpilih"
    
    def deactivate_photos(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} foto berhasil dinonaktifkan.")
    deactivate_photos.short_description = "Nonaktifkan foto terpilih"


# VillageGeography and GoogleMapsEmblem admin classes removed - models not available

# Kustomisasi Admin Site
admin.site.site_header = "Admin Sejarah Desa Pulosarok"
admin.site.site_title = "Sejarah Desa Admin"
admin.site.index_title = "Kelola Data Sejarah Desa"