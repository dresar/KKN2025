from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    PerangkatDesa, LembagaAdat, PenggerakPKK, 
    Kepemudaan, KarangTaruna
)


@admin.register(PerangkatDesa)
class PerangkatDesaAdmin(admin.ModelAdmin):
    list_display = ['get_nama_lengkap', 'jabatan', 'status', 'tanggal_mulai_tugas', 'get_masa_kerja', 'get_foto_thumbnail']
    list_filter = ['jabatan', 'status', 'tanggal_mulai_tugas', 'created_at']
    search_fields = ['penduduk__name', 'jabatan', 'nip', 'penduduk__nik']
    ordering = ['jabatan', 'penduduk__name']
    raw_id_fields = ['penduduk']
    readonly_fields = ['created_at', 'updated_at', 'get_foto_preview']
    list_per_page = 25
    date_hierarchy = 'tanggal_mulai_tugas'
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('penduduk', 'jabatan', 'status')
        }),
        ('Detail Kepegawaian', {
            'fields': ('nip', 'sk_pengangkatan', 'tanggal_mulai_tugas', 'tanggal_selesai_tugas')
        }),
        ('Kompensasi', {
            'fields': ('gaji_pokok', 'tunjangan'),
            'classes': ('collapse',)
        }),
        ('Informasi Tambahan', {
            'fields': ('deskripsi_tugas', 'foto_profil', 'get_foto_preview', 'kontak_whatsapp', 'email_dinas')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_nama_lengkap(self, obj):
        return obj.penduduk.name
    get_nama_lengkap.short_description = 'Nama Lengkap'
    get_nama_lengkap.admin_order_field = 'penduduk__name'
    
    def get_masa_kerja(self, obj):
        from datetime import date
        if obj.tanggal_selesai_tugas:
            delta = obj.tanggal_selesai_tugas - obj.tanggal_mulai_tugas
        else:
            delta = date.today() - obj.tanggal_mulai_tugas
        years = delta.days // 365
        months = (delta.days % 365) // 30
        return f"{years} tahun {months} bulan"
    get_masa_kerja.short_description = 'Masa Kerja'
    
    def get_foto_thumbnail(self, obj):
        if obj.foto_profil:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%;" />', obj.foto_profil.url)
        return '-'
    get_foto_thumbnail.short_description = 'Foto'
    
    def get_foto_preview(self, obj):
        if obj.foto_profil:
            return format_html('<img src="{}" width="150" height="150" style="border-radius: 10px;" />', obj.foto_profil.url)
        return 'Tidak ada foto'
    get_foto_preview.short_description = 'Preview Foto'


@admin.register(LembagaAdat)
class LembagaAdatAdmin(admin.ModelAdmin):
    list_display = ['nama_lembaga', 'jenis_lembaga', 'get_ketua_nama', 'status', 'jumlah_anggota', 'tanggal_terbentuk', 'get_foto_thumbnail']
    list_filter = ['jenis_lembaga', 'status', 'tanggal_terbentuk', 'created_at']
    search_fields = ['nama_lembaga', 'deskripsi', 'ketua__name', 'alamat_sekretariat']
    ordering = ['nama_lembaga']
    raw_id_fields = ['ketua', 'sekretaris', 'bendahara']
    readonly_fields = ['created_at', 'updated_at', 'get_foto_preview']
    list_per_page = 25
    date_hierarchy = 'tanggal_terbentuk'
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('nama_lembaga', 'jenis_lembaga', 'status', 'tanggal_terbentuk')
        }),
        ('Struktur Kepengurusan', {
            'fields': ('ketua', 'sekretaris', 'bendahara')
        }),
        ('Detail Organisasi', {
            'fields': ('deskripsi', 'kegiatan_rutin', 'jumlah_anggota', 'alamat_sekretariat')
        }),
        ('Kontak & Media', {
            'fields': ('kontak_phone', 'foto_kegiatan', 'get_foto_preview')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_ketua_nama(self, obj):
        return obj.ketua.name if obj.ketua else '-'
    get_ketua_nama.short_description = 'Ketua'
    get_ketua_nama.admin_order_field = 'ketua__name'
    
    def get_foto_thumbnail(self, obj):
        if obj.foto_kegiatan:
            return format_html('<img src="{}" width="40" height="30" style="border-radius: 5px;" />', obj.foto_kegiatan.url)
        return '-'
    get_foto_thumbnail.short_description = 'Foto'
    
    def get_foto_preview(self, obj):
        if obj.foto_kegiatan:
            return format_html('<img src="{}" width="200" height="150" style="border-radius: 10px;" />', obj.foto_kegiatan.url)
        return 'Tidak ada foto'
    get_foto_preview.short_description = 'Preview Foto'


@admin.register(PenggerakPKK)
class PenggerakPKKAdmin(admin.ModelAdmin):
    list_display = ['get_nama_lengkap', 'jabatan', 'status', 'tanggal_bergabung', 'nomor_anggota', 'get_masa_bergabung', 'get_foto_thumbnail']
    list_filter = ['jabatan', 'status', 'tanggal_bergabung', 'created_at']
    search_fields = ['penduduk__name', 'nomor_anggota', 'keahlian', 'penduduk__nik']
    ordering = ['jabatan', 'penduduk__name']
    raw_id_fields = ['penduduk']
    readonly_fields = ['created_at', 'updated_at', 'get_foto_preview']
    list_per_page = 25
    date_hierarchy = 'tanggal_bergabung'
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('penduduk', 'jabatan', 'status', 'nomor_anggota')
        }),
        ('Periode Keanggotaan', {
            'fields': ('tanggal_bergabung', 'tanggal_keluar')
        }),
        ('Profil Anggota', {
            'fields': ('keahlian', 'pengalaman_organisasi', 'prestasi', 'foto_profil', 'get_foto_preview')
        }),
        ('Kontak', {
            'fields': ('kontak_whatsapp', 'alamat_lengkap')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_nama_lengkap(self, obj):
        return obj.penduduk.name
    get_nama_lengkap.short_description = 'Nama Lengkap'
    get_nama_lengkap.admin_order_field = 'penduduk__name'
    
    def get_masa_bergabung(self, obj):
        from datetime import date
        if obj.tanggal_keluar:
            delta = obj.tanggal_keluar - obj.tanggal_bergabung
        else:
            delta = date.today() - obj.tanggal_bergabung
        years = delta.days // 365
        months = (delta.days % 365) // 30
        return f"{years} tahun {months} bulan"
    get_masa_bergabung.short_description = 'Masa Bergabung'
    
    def get_foto_thumbnail(self, obj):
        if obj.foto_profil:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%;" />', obj.foto_profil.url)
        return '-'
    get_foto_thumbnail.short_description = 'Foto'
    
    def get_foto_preview(self, obj):
        if obj.foto_profil:
            return format_html('<img src="{}" width="150" height="150" style="border-radius: 10px;" />', obj.foto_profil.url)
        return 'Tidak ada foto'
    get_foto_preview.short_description = 'Preview Foto'


@admin.register(Kepemudaan)
class KepemudaanAdmin(admin.ModelAdmin):
    list_display = ['nama_organisasi', 'jenis_organisasi', 'get_ketua_nama', 'status', 'jumlah_anggota_aktif', 'tanggal_terbentuk', 'get_foto_thumbnail']
    list_filter = ['jenis_organisasi', 'status', 'tanggal_terbentuk', 'created_at']
    search_fields = ['nama_organisasi', 'deskripsi', 'ketua__name', 'alamat_sekretariat']
    ordering = ['nama_organisasi']
    raw_id_fields = ['ketua', 'sekretaris', 'bendahara']
    readonly_fields = ['created_at', 'updated_at', 'get_foto_preview']
    list_per_page = 25
    date_hierarchy = 'tanggal_terbentuk'
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('nama_organisasi', 'jenis_organisasi', 'status', 'tanggal_terbentuk')
        }),
        ('Struktur Kepengurusan', {
            'fields': ('ketua', 'sekretaris', 'bendahara')
        }),
        ('Detail Organisasi', {
            'fields': ('deskripsi', 'kegiatan_rutin', 'prestasi', 'jumlah_anggota_aktif', 'rentang_usia')
        }),
        ('Kontak & Lokasi', {
            'fields': ('alamat_sekretariat', 'kontak_phone', 'email', 'foto_kegiatan', 'get_foto_preview')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_ketua_nama(self, obj):
        return obj.ketua.name if obj.ketua else '-'
    get_ketua_nama.short_description = 'Ketua'
    get_ketua_nama.admin_order_field = 'ketua__name'
    
    def get_foto_thumbnail(self, obj):
        if obj.foto_kegiatan:
            return format_html('<img src="{}" width="40" height="30" style="border-radius: 5px;" />', obj.foto_kegiatan.url)
        return '-'
    get_foto_thumbnail.short_description = 'Foto'
    
    def get_foto_preview(self, obj):
        if obj.foto_kegiatan:
            return format_html('<img src="{}" width="200" height="150" style="border-radius: 10px;" />', obj.foto_kegiatan.url)
        return 'Tidak ada foto'
    get_foto_preview.short_description = 'Preview Foto'


@admin.register(KarangTaruna)
class KarangTarunaAdmin(admin.ModelAdmin):
    list_display = ['get_nama_lengkap', 'jabatan', 'nomor_anggota', 'status', 'is_pengurus_inti', 'tanggal_bergabung', 'get_masa_bergabung', 'get_foto_thumbnail']
    list_filter = ['jabatan', 'status', 'is_pengurus_inti', 'tanggal_bergabung', 'created_at']
    search_fields = ['penduduk__name', 'nomor_anggota', 'bidang_keahlian', 'pekerjaan', 'penduduk__nik']
    ordering = ['jabatan', 'penduduk__name']
    raw_id_fields = ['penduduk']
    readonly_fields = ['created_at', 'updated_at', 'get_foto_preview']
    list_per_page = 25
    date_hierarchy = 'tanggal_bergabung'
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('penduduk', 'jabatan', 'nomor_anggota', 'status', 'is_pengurus_inti')
        }),
        ('Periode Keanggotaan', {
            'fields': ('tanggal_bergabung', 'tanggal_keluar')
        }),
        ('Profil Anggota', {
            'fields': ('bidang_keahlian', 'pengalaman_organisasi', 'prestasi_individu', 'kontribusi')
        }),
        ('Data Pribadi', {
            'fields': ('pendidikan_terakhir', 'pekerjaan', 'foto_profil', 'get_foto_preview')
        }),
        ('Kontak', {
            'fields': ('kontak_whatsapp', 'email_pribadi', 'alamat_lengkap')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_nama_lengkap(self, obj):
        return obj.penduduk.name
    get_nama_lengkap.short_description = 'Nama Lengkap'
    get_nama_lengkap.admin_order_field = 'penduduk__name'
    
    def get_masa_bergabung(self, obj):
        from datetime import date
        if obj.tanggal_keluar:
            delta = obj.tanggal_keluar - obj.tanggal_bergabung
        else:
            delta = date.today() - obj.tanggal_bergabung
        years = delta.days // 365
        months = (delta.days % 365) // 30
        return f"{years} tahun {months} bulan"
    get_masa_bergabung.short_description = 'Masa Bergabung'
    
    def get_foto_thumbnail(self, obj):
        if obj.foto_profil:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%;" />', obj.foto_profil.url)
        return '-'
    get_foto_thumbnail.short_description = 'Foto'
    
    def get_foto_preview(self, obj):
        if obj.foto_profil:
            return format_html('<img src="{}" width="150" height="150" style="border-radius: 10px;" />', obj.foto_profil.url)
        return 'Tidak ada foto'
    get_foto_preview.short_description = 'Preview Foto'