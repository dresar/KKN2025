from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()

class TourismCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nama Kategori")
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icon FontAwesome")
    color = models.CharField(max_length=7, default="#3B82F6", verbose_name="Warna")
    image = models.ImageField(upload_to='tourism/categories/', blank=True, null=True, verbose_name="Gambar Kategori")
    video = models.FileField(upload_to='tourism/categories/videos/', blank=True, null=True, verbose_name="Video Kategori")
    youtube_link = models.URLField(blank=True, null=True, verbose_name="Link YouTube")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kategori Wisata"
        verbose_name_plural = "Kategori Wisata"
        ordering = ['name']

    def __str__(self):
        return self.name

class TourismLocation(models.Model):
    LOCATION_TYPE_CHOICES = [
        ('natural', 'Wisata Alam'),
        ('cultural', 'Wisata Budaya'),
        ('historical', 'Wisata Sejarah'),
        ('religious', 'Wisata Religi'),
        ('culinary', 'Wisata Kuliner'),
        ('adventure', 'Wisata Petualangan'),
        ('education', 'Wisata Edukasi'),
        ('other', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Dipublikasi'),
        ('archived', 'Diarsipkan'),
    ]

    title = models.CharField(max_length=200, verbose_name="Judul Wisata")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug URL")
    category = models.ForeignKey(TourismCategory, on_delete=models.CASCADE, verbose_name="Kategori")
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES, default='natural', verbose_name="Jenis Wisata")
    
    # Deskripsi
    short_description = models.TextField(max_length=500, verbose_name="Deskripsi Singkat")
    full_description = models.TextField(verbose_name="Deskripsi Lengkap")
    
    # Lokasi
    address = models.TextField(verbose_name="Alamat Lengkap")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Longitude")
    
    # Informasi Wisata
    opening_hours = models.CharField(max_length=200, blank=True, verbose_name="Jam Buka")
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Biaya Masuk")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Nomor Telepon")
    contact_email = models.EmailField(blank=True, verbose_name="Email")
    website = models.URLField(blank=True, verbose_name="Website")
    
    # Fitur dan Fasilitas
    facilities = models.JSONField(default=list, blank=True, verbose_name="Fasilitas")
    activities = models.JSONField(default=list, blank=True, verbose_name="Aktivitas yang Tersedia")
    
    # Status dan Meta
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Status")
    featured = models.BooleanField(default=False, verbose_name="Wisata Unggulan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Gambar Utama
    main_image = models.ImageField(upload_to='tourism/locations/', null=True, blank=True, verbose_name="Gambar Utama")
    
    # SEO dan Meta
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta Keywords")
    
    # Timestamps
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tourism_created', verbose_name="Dibuat Oleh")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tourism_updated', verbose_name="Diupdate Oleh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Tanggal Publikasi")

    class Meta:
        verbose_name = "Lokasi Wisata"
        verbose_name_plural = "Lokasi Wisata"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
            
    @property
    def get_featured_image(self):
        """Return the featured image for this location"""
        if self.main_image:
            return self.main_image.url
        
        # Try to get a featured image from gallery
        featured_image = self.gallery.filter(is_active=True, is_featured=True, media_type='image').first()
        if featured_image:
            return featured_image.file.url
        
        # Otherwise get the first image from gallery
        first_image = self.gallery.filter(is_active=True, media_type='image').first()
        if first_image:
            return first_image.file.url
        
        # Return a placeholder if no image is available
        return '/static/img/placeholder.jpg'
    
    @property
    def location_type_display(self):
        """Return the display value of location_type"""
        return dict(self.LOCATION_TYPE_CHOICES).get(self.location_type, self.location_type)
        
    @property
    def average_rating(self):
        """Calculate the average rating for this location"""
        from django.db.models import Avg
        # Get average from TourismReview
        reviews = self.reviews.filter(is_active=True)
        if reviews.exists():
            return reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        return 0
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0

    @property
    def total_reviews(self):
        return self.ratings.count()
        
    @property
    def get_featured_image(self):
        if self.main_image:
            return self.main_image
        # Try to get featured image from gallery
        featured_gallery = self.gallery.filter(is_featured=True).first()
        if featured_gallery and featured_gallery.image:
            return featured_gallery.image
        # Get first image from gallery
        first_gallery = self.gallery.filter(media_type='image').first()
        if first_gallery and first_gallery.image:
            return first_gallery.image
        return None
        
    @property
    def location_type_display(self):
        return self.get_location_type_display()

class TourismGallery(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Gambar'),
        ('video', 'Video'),
        ('360', 'Foto 360°'),
    ]

    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='gallery', verbose_name="Lokasi Wisata")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image', verbose_name="Jenis Media")
    title = models.CharField(max_length=200, verbose_name="Judul")
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    
    # Media files
    image = models.ImageField(upload_to='tourism/gallery/', null=True, blank=True, verbose_name="Gambar")
    video_url = models.URLField(blank=True, verbose_name="URL Video")
    video_file = models.FileField(upload_to='tourism/videos/', null=True, blank=True, verbose_name="File Video")
    
    # Metadata
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Alt Text")
    caption = models.CharField(max_length=300, blank=True, verbose_name="Caption")
    is_featured = models.BooleanField(default=False, verbose_name="Gambar Unggulan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Ordering
    order = models.PositiveIntegerField(default=0, verbose_name="Urutan")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Galeri Wisata"
        verbose_name_plural = "Galeri Wisata"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.tourism_location.title}"

class TourismReview(models.Model):
    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='reviews', verbose_name="Lokasi Wisata")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Pengguna")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Rating")
    title = models.CharField(max_length=200, verbose_name="Judul Review")
    comment = models.TextField(verbose_name="Komentar")
    
    # Review details
    visit_date = models.DateField(null=True, blank=True, verbose_name="Tanggal Kunjungan")
    visit_type = models.CharField(max_length=20, choices=[
        ('personal', 'Pribadi'),
        ('family', 'Keluarga'),
        ('group', 'Grup'),
        ('business', 'Bisnis'),
    ], default='personal', verbose_name="Jenis Kunjungan")
    
    # Moderation
    is_approved = models.BooleanField(default=False, verbose_name="Disetujui")
    is_flagged = models.BooleanField(default=False, verbose_name="Ditandai")
    flagged_reason = models.TextField(blank=True, verbose_name="Alasan Ditandai")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review Wisata"
        verbose_name_plural = "Review Wisata"
        ordering = ['-created_at']
        unique_together = ['tourism_location', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.tourism_location.title}"

class TourismRating(models.Model):
    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='ratings', verbose_name="Lokasi Wisata")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Pengguna")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Rating")
    
    # Rating categories
    cleanliness = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, verbose_name="Kebersihan")
    accessibility = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, verbose_name="Aksesibilitas")
    facilities = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, verbose_name="Fasilitas")
    service = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, verbose_name="Pelayanan")
    value = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, verbose_name="Nilai")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rating Wisata"
        verbose_name_plural = "Rating Wisata"
        unique_together = ['tourism_location', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.tourism_location.title} ({self.rating}/5)"

class TourismEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('festival', 'Festival'),
        ('exhibition', 'Pameran'),
        ('workshop', 'Workshop'),
        ('competition', 'Kompetisi'),
        ('ceremony', 'Upacara'),
        ('other', 'Lainnya'),
    ]

    title = models.CharField(max_length=200, verbose_name="Judul Event")
    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='events', verbose_name="Lokasi Wisata")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='festival', verbose_name="Jenis Event")
    
    # Event details
    description = models.TextField(verbose_name="Deskripsi Event")
    start_date = models.DateTimeField(verbose_name="Tanggal Mulai")
    end_date = models.DateTimeField(verbose_name="Tanggal Selesai")
    
    # Event info
    organizer = models.CharField(max_length=200, blank=True, verbose_name="Penyelenggara")
    contact_info = models.TextField(blank=True, verbose_name="Informasi Kontak")
    registration_required = models.BooleanField(default=False, verbose_name="Pendaftaran Diperlukan")
    registration_url = models.URLField(blank=True, verbose_name="URL Pendaftaran")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_featured = models.BooleanField(default=False, verbose_name="Event Unggulan")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event Wisata"
        verbose_name_plural = "Event Wisata"
        ordering = ['start_date']

    def __str__(self):
        return f"{self.title} - {self.tourism_location.title}"

class TourismPackage(models.Model):
    PACKAGE_TYPE_CHOICES = [
        ('day_trip', 'Perjalanan Sehari'),
        ('weekend', 'Paket Weekend'),
        ('week_long', 'Paket Seminggu'),
        ('custom', 'Paket Kustom'),
    ]

    title = models.CharField(max_length=200, verbose_name="Judul Paket")
    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='packages', verbose_name="Lokasi Wisata")
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES, default='day_trip', verbose_name="Jenis Paket")
    
    # Package details
    description = models.TextField(verbose_name="Deskripsi Paket")
    duration = models.CharField(max_length=100, verbose_name="Durasi")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Harga")
    currency = models.CharField(max_length=3, default='IDR', verbose_name="Mata Uang")
    
    # Contact info
    whatsapp = models.CharField(max_length=20, blank=True, null=True, verbose_name="Nomor WhatsApp")
    
    # Media
    image = models.ImageField(upload_to='tourism/packages/', null=True, blank=True, verbose_name="Gambar Paket")
    video = models.FileField(upload_to='tourism/packages/videos/', null=True, blank=True, verbose_name="Video Paket")
    youtube_link = models.URLField(blank=True, null=True, verbose_name="Link YouTube")
    
    # Package features
    includes = models.JSONField(default=list, verbose_name="Yang Termasuk")
    excludes = models.JSONField(default=list, verbose_name="Yang Tidak Termasuk")
    itinerary = models.JSONField(default=list, verbose_name="Itinerary")
    
    # Booking info
    max_participants = models.PositiveIntegerField(null=True, blank=True, verbose_name="Maksimal Peserta")
    min_participants = models.PositiveIntegerField(default=1, verbose_name="Minimal Peserta")
    booking_deadline = models.PositiveIntegerField(default=7, verbose_name="Deadline Booking (hari)")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_featured = models.BooleanField(default=False, verbose_name="Paket Unggulan")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paket Wisata"
        verbose_name_plural = "Paket Wisata"
        ordering = ['price']

    def __str__(self):
        return f"{self.title} - {self.tourism_location.title}"

class TourismGallery(models.Model):
    package = models.ForeignKey(TourismPackage, on_delete=models.CASCADE, related_name='gallery', verbose_name="Paket Wisata")
    image = models.ImageField(upload_to='tourism/packages/gallery/', verbose_name="Gambar")
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Judul Gambar")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi Gambar")
    order = models.PositiveIntegerField(default=0, verbose_name="Urutan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Galeri Paket Wisata"
        verbose_name_plural = "Galeri Paket Wisata"
        ordering = ['order']

    def __str__(self):
        return f"Gambar {self.order} - {self.package.title}"

class TourismFAQ(models.Model):
    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='faqs', verbose_name="Lokasi Wisata")
    question = models.TextField(verbose_name="Pertanyaan")
    answer = models.TextField(verbose_name="Jawaban")
    
    # FAQ metadata
    category = models.CharField(max_length=100, blank=True, verbose_name="Kategori")
    order = models.PositiveIntegerField(default=0, verbose_name="Urutan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ Wisata"
        verbose_name_plural = "FAQ Wisata"
        ordering = ['order', 'question']

    def __str__(self):
        return f"{self.question[:50]}... - {self.tourism_location.title}"
