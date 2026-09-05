from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from references.models import Penduduk
import json
import uuid
from cryptography.fernet import Fernet
from django.conf import settings

User = get_user_model()


class LetterType(models.Model):
    """Model untuk jenis surat"""
    name = models.CharField(max_length=100, verbose_name='Nama Jenis Surat')
    code = models.CharField(max_length=20, unique=True, verbose_name='Kode Surat')
    description = models.TextField(blank=True, verbose_name='Deskripsi')
    template_file = models.FileField(
        upload_to='letter_templates/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['docx', 'pdf'])],
        verbose_name='File Template'
    )
    required_documents = models.TextField(
        blank=True,
        help_text='Dokumen yang diperlukan (pisahkan dengan koma)',
        verbose_name='Dokumen yang Diperlukan'
    )
    processing_time_days = models.PositiveIntegerField(
        default=3,
        verbose_name='Waktu Proses (Hari)'
    )
    fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Biaya'
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Jenis Surat'
        verbose_name_plural = 'Jenis Surat'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Letter(models.Model):
    """Model untuk surat"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Diajukan'),
        ('in_review', 'Sedang Ditinjau'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Rendah'),
        ('normal', 'Normal'),
        ('high', 'Tinggi'),
        ('urgent', 'Mendesak'),
    ]

    letter_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name='Nomor Surat'
    )
    letter_type = models.ForeignKey(
        LetterType,
        on_delete=models.CASCADE,
        verbose_name='Jenis Surat'
    )
    applicant = models.ForeignKey(
        Penduduk,
        on_delete=models.CASCADE,
        verbose_name='Pemohon'
    )
    subject = models.CharField(max_length=200, verbose_name='Perihal')
    content = models.TextField(verbose_name='Isi Surat')
    purpose = models.TextField(verbose_name='Tujuan Penggunaan')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Status'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name='Prioritas'
    )
    submission_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Tanggal Pengajuan'
    )
    approval_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Tanggal Persetujuan'
    )
    completion_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Tanggal Selesai'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='approved_letters',
        verbose_name='Disetujui Oleh'
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='Alasan Penolakan'
    )
    notes = models.TextField(blank=True, verbose_name='Catatan')
    
    # AI and Template fields
    template = models.ForeignKey(
        'LetterTemplate',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Template Surat'
    )
    ai_generated_content = models.TextField(
        blank=True,
        verbose_name='Konten yang Dihasilkan AI'
    )
    ai_suggestions_applied = models.JSONField(
        default=list,
        verbose_name='Saran AI yang Diterapkan'
    )
    requires_ai_validation = models.BooleanField(
        default=True,
        verbose_name='Memerlukan Validasi AI'
    )
    
    # Digital signature fields
    requires_digital_signature = models.BooleanField(
        default=False,
        verbose_name='Memerlukan Tanda Tangan Digital'
    )
    is_digitally_signed = models.BooleanField(
        default=False,
        verbose_name='Sudah Ditandatangani Digital'
    )
    signature_hash = models.CharField(
        max_length=256,
        blank=True,
        verbose_name='Hash Dokumen untuk Tanda Tangan'
    )
    
    # Export and sharing
    pdf_file = models.FileField(
        upload_to='letter_pdfs/',
        blank=True,
        null=True,
        verbose_name='File PDF'
    )
    qr_code = models.ImageField(
        upload_to='letter_qrcodes/',
        blank=True,
        null=True,
        verbose_name='QR Code untuk Verifikasi'
    )
    public_url = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        verbose_name='URL Publik'
    )
    
    # Metadata
    word_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Jumlah Kata'
    )
    estimated_reading_time = models.PositiveIntegerField(
        default=0,
        verbose_name='Estimasi Waktu Baca (detik)'
    )
    language = models.CharField(
        max_length=10,
        default='id',
        verbose_name='Bahasa'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_letters',
        verbose_name='Dibuat Oleh'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Surat'
        verbose_name_plural = 'Surat'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.letter_number or 'Draft'} - {self.subject}"

    def save(self, *args, **kwargs):
        # Generate letter number using LetterSettings
        if not self.letter_number and self.status != 'draft':
            try:
                letter_settings = LetterSettings.objects.filter(is_active=True).first()
                if letter_settings:
                    self.letter_number = letter_settings.get_next_letter_number(self.letter_type.code)
                else:
                    # Fallback to old method
                    year = timezone.now().year
                    month = timezone.now().month
                    count = Letter.objects.filter(
                        created_at__year=year,
                        created_at__month=month
                    ).count() + 1
                    self.letter_number = f"{self.letter_type.code}/{count:03d}/{month:02d}/{year}"
            except:
                # Fallback to old method if LetterSettings not available
                year = timezone.now().year
                month = timezone.now().month
                count = Letter.objects.filter(
                    created_at__year=year,
                    created_at__month=month
                ).count() + 1
                self.letter_number = f"{self.letter_type.code}/{count:03d}/{month:02d}/{year}"
        
        # Generate public URL if not exists
        if not self.public_url:
            self.public_url = str(uuid.uuid4())[:8]
        
        # Calculate word count and reading time
        if self.content:
            self.word_count = len(self.content.split())
            # Average reading speed: 200 words per minute
            self.estimated_reading_time = max(1, (self.word_count * 60) // 200)
        
        super().save(*args, **kwargs)
        
        # Generate QR code after saving (when we have an ID)
        if self.pk and not self.qr_code:
            self.generate_qr_code()
    
    def generate_qr_code(self):
        """Generate QR code for letter verification"""
        try:
            import qrcode
            from io import BytesIO
            from django.core.files import File
            
            # Create verification URL
            verification_url = f"https://pulosarok.desa.id/verify/{self.public_url}"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(verification_url)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Save to model
            filename = f"qr_{self.public_url}.png"
            self.qr_code.save(filename, File(buffer), save=False)
            self.save(update_fields=['qr_code'])
            
        except ImportError:
            pass  # QR code library not installed
        except Exception as e:
            pass  # Handle any other errors silently
    
    def generate_pdf(self):
        """Generate PDF version of the letter"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from io import BytesIO
            from django.core.files import File
            
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            
            # Get letter settings for header
            letter_settings = LetterSettings.objects.filter(is_active=True).first()
            
            # Add content to PDF
            y_position = 750
            
            if letter_settings:
                # Header
                p.setFont("Helvetica-Bold", 16)
                p.drawString(100, y_position, letter_settings.village_name)
                y_position -= 20
                p.setFont("Helvetica", 12)
                p.drawString(100, y_position, letter_settings.village_address)
                y_position -= 40
            
            # Letter number and date
            p.setFont("Helvetica", 12)
            p.drawString(100, y_position, f"Nomor: {self.letter_number or 'Draft'}")
            y_position -= 20
            p.drawString(100, y_position, f"Tanggal: {self.created_at.strftime('%d %B %Y')}")
            y_position -= 40
            
            # Subject
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, y_position, f"Perihal: {self.subject}")
            y_position -= 40
            
            # Content
            p.setFont("Helvetica", 12)
            # Simple text wrapping
            lines = self.content.split('\n')
            for line in lines:
                if y_position < 100:  # Start new page if needed
                    p.showPage()
                    y_position = 750
                p.drawString(100, y_position, line[:80])  # Limit line length
                y_position -= 15
            
            # Signature area
            if letter_settings and y_position > 150:
                y_position -= 40
                p.drawString(400, y_position, f"{letter_settings.village_name}")
                y_position -= 20
                p.drawString(400, y_position, f"Kepala Desa")
                y_position -= 60
                p.drawString(400, y_position, f"{letter_settings.head_of_village_name}")
            
            p.save()
            buffer.seek(0)
            
            # Save PDF file
            filename = f"letter_{self.public_url}.pdf"
            self.pdf_file.save(filename, File(buffer), save=False)
            self.save(update_fields=['pdf_file'])
            
            return True
            
        except ImportError:
            return False  # ReportLab not installed
        except Exception as e:
            return False
    
    def get_verification_url(self):
        """Get public verification URL"""
        return f"https://pulosarok.desa.id/verify/{self.public_url}"
    
    def calculate_similarity_score(self, other_content):
        """Calculate similarity score with another content"""
        try:
            from difflib import SequenceMatcher
            return SequenceMatcher(None, self.content, other_content).ratio()
        except:
            return 0.0
    
    def get_ai_validation_status(self):
        """Get AI validation status"""
        try:
            return self.ai_validation.status
        except:
            return 'not_validated'
    
    def is_ai_validated(self):
        """Check if letter passed AI validation"""
        try:
            return self.ai_validation.is_valid()
        except:
            return False


class LetterRecipient(models.Model):
    """Model untuk penerima surat"""
    RECIPIENT_TYPE_CHOICES = [
        ('internal', 'Internal'),
        ('external', 'Eksternal'),
        ('government', 'Instansi Pemerintah'),
        ('private', 'Swasta'),
        ('individual', 'Perorangan'),
    ]

    letter = models.ForeignKey(
        Letter,
        on_delete=models.CASCADE,
        related_name='recipients',
        verbose_name='Surat'
    )
    recipient_type = models.CharField(
        max_length=20,
        choices=RECIPIENT_TYPE_CHOICES,
        verbose_name='Jenis Penerima'
    )
    name = models.CharField(max_length=200, verbose_name='Nama Penerima')
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Jabatan'
    )
    organization = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Organisasi/Instansi'
    )
    address = models.TextField(verbose_name='Alamat')
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telepon'
    )
    email = models.EmailField(blank=True, verbose_name='Email')
    is_primary = models.BooleanField(
        default=False,
        verbose_name='Penerima Utama'
    )
    delivery_method = models.CharField(
        max_length=20,
        choices=[
            ('hand_delivery', 'Antar Langsung'),
            ('post', 'Pos'),
            ('email', 'Email'),
            ('fax', 'Fax'),
        ],
        default='hand_delivery',
        verbose_name='Metode Pengiriman'
    )
    delivery_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Tanggal Pengiriman'
    )
    received_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Tanggal Diterima'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Penerima Surat'
        verbose_name_plural = 'Penerima Surat'
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return f"{self.name} - {self.letter.subject}"


class LetterAttachment(models.Model):
    """Model untuk lampiran surat"""
    ATTACHMENT_TYPE_CHOICES = [
        ('supporting_document', 'Dokumen Pendukung'),
        ('identity_card', 'Kartu Identitas'),
        ('certificate', 'Sertifikat'),
        ('photo', 'Foto'),
        ('other', 'Lainnya'),
    ]

    letter = models.ForeignKey(
        Letter,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Surat'
    )
    attachment_type = models.CharField(
        max_length=30,
        choices=ATTACHMENT_TYPE_CHOICES,
        verbose_name='Jenis Lampiran'
    )
    title = models.CharField(max_length=200, verbose_name='Judul Lampiran')
    description = models.TextField(blank=True, verbose_name='Deskripsi')
    file = models.FileField(
        upload_to='letter_attachments/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])],
        verbose_name='File'
    )
    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Ukuran File (bytes)'
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name='Wajib'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Diunggah Oleh'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lampiran Surat'
        verbose_name_plural = 'Lampiran Surat'
        ordering = ['-is_required', 'title']

    def __str__(self):
        return f"{self.title} - {self.letter.subject}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class LetterTracking(models.Model):
    """Model untuk tracking status surat"""
    ACTION_CHOICES = [
        ('created', 'Dibuat'),
        ('submitted', 'Diajukan'),
        ('reviewed', 'Ditinjau'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('completed', 'Diselesaikan'),
        ('cancelled', 'Dibatalkan'),
        ('sent', 'Dikirim'),
        ('received', 'Diterima'),
        ('returned', 'Dikembalikan'),
    ]

    letter = models.ForeignKey(
        Letter,
        on_delete=models.CASCADE,
        related_name='tracking_history',
        verbose_name='Surat'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Aksi'
    )
    description = models.TextField(verbose_name='Deskripsi')
    performed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Dilakukan Oleh'
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Lokasi'
    )
    notes = models.TextField(blank=True, verbose_name='Catatan')
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='Alamat IP'
    )

    class Meta:
        verbose_name = 'Tracking Surat'
        verbose_name_plural = 'Tracking Surat'
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.letter.subject} - {self.get_action_display()}"


class APIKeySettings(models.Model):
    """Model untuk menyimpan API key Gemini dan konfigurasi AI"""
    service_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nama Layanan'
    )
    api_key = models.TextField(verbose_name='API Key (Encrypted)')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    max_requests_per_day = models.PositiveIntegerField(
        default=1000,
        verbose_name='Maksimal Request per Hari'
    )
    current_usage = models.PositiveIntegerField(
        default=0,
        verbose_name='Penggunaan Hari Ini'
    )
    last_reset_date = models.DateField(
        auto_now_add=True,
        verbose_name='Tanggal Reset Terakhir'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Dibuat Oleh'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pengaturan API Key'
        verbose_name_plural = 'Pengaturan API Key'
        ordering = ['service_name']

    def __str__(self):
        return f"{self.service_name} - {'Aktif' if self.is_active else 'Nonaktif'}"
    
    def set_api_key(self, api_key):
        """Encrypt and store API key"""
        try:
            # Generate encryption key from Django secret key
            key = Fernet.generate_key()
            cipher_suite = Fernet(key)
            
            # Encrypt the API key
            encrypted_key = cipher_suite.encrypt(api_key.encode())
            
            # Store encrypted key and encryption key
            self.encrypted_api_key = encrypted_key.decode()
            self.encryption_key = key.decode()
            
        except Exception as e:
            # Fallback: store as plain text (not recommended for production)
            self.encrypted_api_key = api_key
    
    def get_api_key(self):
        """Decrypt and return API key"""
        try:
            if self.encryption_key:
                cipher_suite = Fernet(self.encryption_key.encode())
                decrypted_key = cipher_suite.decrypt(self.encrypted_api_key.encode())
                return decrypted_key.decode()
            else:
                # Fallback: return as plain text
                return self.encrypted_api_key
        except Exception as e:
            return None
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])
    
    def is_valid(self):
        """Check if API key is valid and active"""
        return self.is_active and self.get_api_key() is not None
    
    def get_usage_stats(self):
        """Get usage statistics"""
        return {
            'total_usage': self.usage_count,
            'last_used': self.last_used,
            'created_date': self.created_at,
            'is_active': self.is_active
        }

    def encrypt_api_key(self, raw_key):
        """Encrypt API key before saving"""
        if hasattr(settings, 'ENCRYPTION_KEY'):
            f = Fernet(settings.ENCRYPTION_KEY.encode())
            self.api_key = f.encrypt(raw_key.encode()).decode()
        else:
            self.api_key = raw_key  # Fallback to plain text if no encryption key

    def decrypt_api_key(self):
        """Decrypt API key for use"""
        if hasattr(settings, 'ENCRYPTION_KEY'):
            try:
                f = Fernet(settings.ENCRYPTION_KEY.encode())
                return f.decrypt(self.api_key.encode()).decode()
            except:
                return self.api_key  # Return as is if decryption fails
        return self.api_key

    def can_make_request(self):
        """Check if can make API request based on daily limit"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.last_reset_date < today:
            self.current_usage = 0
            self.last_reset_date = today
            self.save()
        
        return self.current_usage < self.max_requests_per_day

    def increment_usage(self):
        """Increment API usage counter"""
        self.current_usage += 1
        self.save()


class LetterSettings(models.Model):
    """Model untuk konfigurasi surat (kop surat, nomor, kepala desa)"""
    SIGNATURE_TYPE_CHOICES = [
        ('digital', 'Digital'),
        ('image', 'Gambar'),
        ('text', 'Teks'),
    ]

    village_name = models.CharField(
        max_length=100,
        default='Desa Pulosarok',
        verbose_name='Nama Desa'
    )
    village_address = models.TextField(
        default='Kecamatan Pulosarok, Kabupaten Indramayu',
        verbose_name='Alamat Desa'
    )
    village_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telepon Desa'
    )
    village_email = models.EmailField(
        blank=True,
        verbose_name='Email Desa'
    )
    village_website = models.URLField(
        blank=True,
        verbose_name='Website Desa'
    )
    village_logo = models.ImageField(
        upload_to='village_settings/',
        blank=True,
        null=True,
        verbose_name='Logo Desa'
    )
    
    # Kepala Desa
    head_of_village_name = models.CharField(
        max_length=100,
        verbose_name='Nama Kepala Desa'
    )
    head_of_village_nip = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='NIP Kepala Desa'
    )
    head_of_village_signature_type = models.CharField(
        max_length=20,
        choices=SIGNATURE_TYPE_CHOICES,
        default='digital',
        verbose_name='Jenis Tanda Tangan'
    )
    head_of_village_signature_image = models.ImageField(
        upload_to='signatures/',
        blank=True,
        null=True,
        verbose_name='Gambar Tanda Tangan'
    )
    head_of_village_signature_text = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Teks Tanda Tangan'
    )
    
    # Sekretaris Desa
    secretary_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nama Sekretaris Desa'
    )
    secretary_nip = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='NIP Sekretaris'
    )
    secretary_signature_type = models.CharField(
        max_length=20,
        choices=SIGNATURE_TYPE_CHOICES,
        default='digital',
        verbose_name='Jenis Tanda Tangan Sekretaris'
    )
    secretary_signature_image = models.ImageField(
        upload_to='signatures/',
        blank=True,
        null=True,
        verbose_name='Gambar Tanda Tangan Sekretaris'
    )
    
    # Pengaturan Nomor Surat
    letter_number_format = models.CharField(
        max_length=100,
        default='{code}/{number:03d}/{month:02d}/{year}',
        verbose_name='Format Nomor Surat',
        help_text='Gunakan {code}, {number}, {month}, {year} sebagai placeholder'
    )
    current_year_counter = models.PositiveIntegerField(
        default=0,
        verbose_name='Counter Tahun Ini'
    )
    reset_counter_yearly = models.BooleanField(
        default=True,
        verbose_name='Reset Counter Setiap Tahun'
    )
    
    # AI Settings
    enable_ai_validation = models.BooleanField(
        default=True,
        verbose_name='Aktifkan Validasi AI'
    )
    ai_validation_threshold = models.FloatField(
        default=0.8,
        verbose_name='Threshold Validasi AI (0-1)'
    )
    enable_ai_suggestions = models.BooleanField(
        default=True,
        verbose_name='Aktifkan Saran AI'
    )
    
    # Digital Signature Settings
    enable_digital_signature = models.BooleanField(
        default=True,
        verbose_name='Aktifkan Tanda Tangan Digital'
    )
    signature_certificate = models.FileField(
        upload_to='certificates/',
        blank=True,
        null=True,
        verbose_name='Sertifikat Digital'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Dibuat Oleh'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pengaturan Surat'
        verbose_name_plural = 'Pengaturan Surat'
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        return f"Pengaturan {self.village_name}"
    
    def save(self, *args, **kwargs):
        # Only one active settings at a time
        if self.is_active:
            LetterSettings.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def get_next_letter_number(self, letter_type_code):
        """Generate next letter number"""
        from django.utils import timezone
        now = timezone.now()
        
        if self.reset_counter_yearly:
            # Reset counter if new year
            current_year = now.year
            if not hasattr(self, '_last_year') or self._last_year != current_year:
                self.current_year_counter = 0
                self._last_year = current_year
        
        self.current_year_counter += 1
        self.save()
        
        return self.letter_number_format.format(
            code=letter_type_code,
            number=self.current_year_counter,
            month=now.month,
            year=now.year
        )


class LetterTemplate(models.Model):
    """Model untuk template surat"""
    TEMPLATE_TYPE_CHOICES = [
        ('official', 'Surat Resmi'),
        ('certificate', 'Surat Keterangan'),
        ('recommendation', 'Surat Rekomendasi'),
        ('invitation', 'Surat Undangan'),
        ('notification', 'Surat Pemberitahuan'),
        ('custom', 'Template Kustom'),
    ]

    name = models.CharField(max_length=100, verbose_name='Nama Template')
    template_type = models.CharField(
        max_length=20,
        choices=TEMPLATE_TYPE_CHOICES,
        verbose_name='Jenis Template'
    )
    description = models.TextField(blank=True, verbose_name='Deskripsi')
    content_template = models.TextField(
        verbose_name='Template Konten',
        help_text='Gunakan {{variable}} untuk placeholder'
    )
    variables = models.JSONField(
        default=dict,
        verbose_name='Variabel Template',
        help_text='JSON object dengan daftar variabel yang tersedia'
    )
    css_styles = models.TextField(
        blank=True,
        verbose_name='CSS Styles',
        help_text='CSS untuk styling template'
    )
    header_template = models.TextField(
        blank=True,
        verbose_name='Template Header'
    )
    footer_template = models.TextField(
        blank=True,
        verbose_name='Template Footer'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Template Default'
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Jumlah Penggunaan'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Dibuat Oleh'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Template Surat'
        verbose_name_plural = 'Template Surat'
        ordering = ['-is_default', '-usage_count', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.save()

    def render_content(self, context):
        """Render template with context variables"""
        import re
        content = self.content_template
        
        # Replace {{variable}} with context values
        for key, value in context.items():
            pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
            content = re.sub(pattern, str(value), content)
        
        return content


class LetterAIValidation(models.Model):
    """Model untuk menyimpan hasil validasi AI"""
    VALIDATION_STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('processing', 'Sedang Diproses'),
        ('completed', 'Selesai'),
        ('failed', 'Gagal'),
    ]

    letter = models.OneToOneField(
        Letter,
        on_delete=models.CASCADE,
        related_name='ai_validation',
        verbose_name='Surat'
    )
    validation_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name='ID Validasi'
    )
    status = models.CharField(
        max_length=20,
        choices=VALIDATION_STATUS_CHOICES,
        default='pending',
        verbose_name='Status Validasi'
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Skor Kepercayaan (0-1)'
    )
    validation_result = models.JSONField(
        default=dict,
        verbose_name='Hasil Validasi'
    )
    suggestions = models.JSONField(
        default=list,
        verbose_name='Saran Perbaikan'
    )
    grammar_check = models.JSONField(
        default=dict,
        verbose_name='Pemeriksaan Tata Bahasa'
    )
    content_analysis = models.JSONField(
        default=dict,
        verbose_name='Analisis Konten'
    )
    processing_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Waktu Proses (ms)'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Pesan Error'
    )
    validated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Waktu Validasi'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Validasi AI Surat'
        verbose_name_plural = 'Validasi AI Surat'
        ordering = ['-created_at']

    def __str__(self):
        return f"Validasi AI - {self.letter.subject} ({self.get_status_display()})"

    def is_valid(self):
        """Check if validation passed based on threshold"""
        if self.confidence_score is None:
            return False
        
        try:
            settings_obj = LetterSettings.objects.filter(is_active=True).first()
            threshold = settings_obj.ai_validation_threshold if settings_obj else 0.8
            return self.confidence_score >= threshold
        except:
            return self.confidence_score >= 0.8
    
    def get_suggestions_list(self):
        """Get suggestions as list"""
        try:
            return self.suggestions if isinstance(self.suggestions, list) else []
        except:
            return []
    
    def add_suggestion(self, suggestion):
        """Add a new suggestion"""
        suggestions = self.get_suggestions_list()
        suggestions.append(suggestion)
        self.suggestions = suggestions
    
    def get_validation_summary(self):
        """Get validation summary"""
        return {
            'status': self.status,
            'confidence': self.confidence_score,
            'suggestions_count': len(self.get_suggestions_list()),
            'validated_at': self.validated_at,
            'processing_time': self.processing_time_ms
        }


class LetterDigitalSignature(models.Model):
    """Model untuk tanda tangan digital"""
    SIGNATURE_STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('signed', 'Ditandatangani'),
        ('verified', 'Terverifikasi'),
        ('invalid', 'Tidak Valid'),
    ]

    letter = models.ForeignKey(
        Letter,
        on_delete=models.CASCADE,
        related_name='digital_signatures',
        verbose_name='Surat'
    )
    signer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Penandatangan'
    )
    signature_hash = models.CharField(
        max_length=256,
        verbose_name='Hash Tanda Tangan'
    )
    signature_data = models.TextField(
        verbose_name='Data Tanda Tangan (Encrypted)'
    )
    certificate_info = models.JSONField(
        default=dict,
        verbose_name='Informasi Sertifikat'
    )
    signature_timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Waktu Tanda Tangan'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='Alamat IP'
    )
    user_agent = models.TextField(
        verbose_name='User Agent'
    )
    status = models.CharField(
        max_length=20,
        choices=SIGNATURE_STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    verification_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Tanggal Verifikasi'
    )
    is_valid = models.BooleanField(
        default=True,
        verbose_name='Valid'
    )

    class Meta:
        verbose_name = 'Tanda Tangan Digital'
        verbose_name_plural = 'Tanda Tangan Digital'
        ordering = ['-signature_timestamp']
        unique_together = ['letter', 'signer']

    def __str__(self):
        return f"Tanda Tangan {self.signer.get_full_name()} - {self.letter.subject}"

    def generate_signature_hash(self):
        """Generate signature hash from letter content"""
        import hashlib
        content = f"{self.letter.subject}{self.letter.content}{self.letter.letter_number}"
        self.signature_hash = hashlib.sha256(content.encode()).hexdigest()
        return self.signature_hash
    
    def verify_signature(self):
        """Verify signature integrity"""
        current_hash = self.generate_signature_hash()
        return current_hash == self.signature_hash
    
    def sign_letter(self, signer_user, certificate_data=None):
        """Sign the letter"""
        self.signer = signer_user
        self.signature_timestamp = timezone.now()
        self.status = 'signed'
        self.generate_signature_hash()
        
        if certificate_data:
            self.certificate_info = certificate_data
        
        self.save()
        
        # Update letter status
        self.letter.is_digitally_signed = True
        self.letter.signature_hash = self.signature_hash
        self.letter.save(update_fields=['is_digitally_signed', 'signature_hash'])
    
    def get_signature_info(self):
        """Get signature information"""
        return {
            'signer': self.signer.get_full_name() if self.signer else None,
            'signed_at': self.signature_timestamp,
            'status': self.status,
            'hash': self.signature_hash,
            'is_valid': self.verify_signature() if self.signature_hash else False
        }
