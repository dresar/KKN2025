from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


# Enhanced Village History models with multi-photo support


class VillageHistory(models.Model):
    """Enhanced Village History with comprehensive features"""
    HISTORY_TYPE_CHOICES = [
        ('FOUNDING', 'Sejarah Berdiri'),
        ('DEVELOPMENT', 'Perkembangan'),
        ('CULTURE', 'Budaya & Tradisi'),
        ('ECONOMY', 'Ekonomi'),
        ('SOCIAL', 'Sosial'),
        ('GOVERNMENT', 'Pemerintahan'),
        ('OTHER', 'Lainnya'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Judul")
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name="Slug")
    summary = models.TextField(max_length=500, blank=True, null=True, verbose_name="Ringkasan", 
                              help_text="Ringkasan singkat sejarah (maksimal 500 karakter)")
    content = models.TextField(verbose_name="Konten Lengkap")
    history_type = models.CharField(max_length=20, choices=HISTORY_TYPE_CHOICES, default='OTHER', verbose_name="Jenis Sejarah")
    
    # Period information
    period_start = models.CharField(max_length=50, blank=True, null=True, verbose_name="Periode Mulai")
    period_end = models.CharField(max_length=50, blank=True, null=True, verbose_name="Periode Berakhir")
    year_start = models.IntegerField(blank=True, null=True, verbose_name="Tahun Mulai",
                                   validators=[MinValueValidator(1000), MaxValueValidator(2100)])
    year_end = models.IntegerField(blank=True, null=True, verbose_name="Tahun Berakhir",
                                 validators=[MinValueValidator(1000), MaxValueValidator(2100)])
    
    # Main image
    featured_image = models.ImageField(upload_to='village_history/featured/', blank=True, null=True, 
                                     verbose_name="Gambar Utama")
    featured_image_caption = models.CharField(max_length=200, blank=True, null=True, 
                                            verbose_name="Keterangan Gambar Utama")
    
    # Additional information
    source = models.CharField(max_length=200, blank=True, null=True, verbose_name="Sumber",
                            help_text="Sumber informasi sejarah")
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name="Penulis")
    
    # Status and metadata
    is_featured = models.BooleanField(default=False, verbose_name="Unggulan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Jumlah Dilihat")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Sejarah Desa"
        verbose_name_plural = "Sejarah Desa"
        ordering = ['-is_featured', 'year_start', 'period_start']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['history_type']),
            models.Index(fields=['year_start']),
        ]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def period_display(self):
        """Display period in a readable format"""
        if self.year_start and self.year_end:
            return f"{self.year_start} - {self.year_end}"
        elif self.year_start:
            return f"Sejak {self.year_start}"
        elif self.period_start and self.period_end:
            return f"{self.period_start} - {self.period_end}"
        elif self.period_start:
            return self.period_start
        return "Periode tidak diketahui"
    
    @property
    def photo_count(self):
        """Get total number of photos"""
        return self.photos.filter(is_active=True).count()


class VillageHistoryPhoto(models.Model):
    """Multiple photos for Village History"""
    history = models.ForeignKey(VillageHistory, on_delete=models.CASCADE, related_name='photos', verbose_name="Sejarah")
    image = models.ImageField(upload_to='village_history/photos/', verbose_name="Foto")
    caption = models.CharField(max_length=200, blank=True, null=True, verbose_name="Keterangan")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    
    # Photo metadata
    photographer = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fotografer")
    photo_date = models.DateField(blank=True, null=True, verbose_name="Tanggal Foto")
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name="Lokasi")
    
    # Display options
    is_featured = models.BooleanField(default=False, verbose_name="Foto Unggulan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Urutan Tampil")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Foto Sejarah"
        verbose_name_plural = "Foto Sejarah"
        ordering = ['display_order', '-is_featured', 'created_at']
        indexes = [
            models.Index(fields=['history', 'is_active']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return f"Foto: {self.history.title} - {self.caption or 'Tanpa keterangan'}"


# VillageMap model removed


# VillageGeography model removed


# GoogleMapsEmblem model removed
