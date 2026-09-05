from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from references.models import Penduduk
import os

User = get_user_model()


class BeneficiaryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    criteria = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Kategori Penerima Bantuan'
        verbose_name_plural = 'Kategori Penerima Bantuan'


class Beneficiary(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
        ('lulus', 'Lulus'),
        ('meninggal', 'Meninggal'),
        ('pindah', 'Pindah'),
    ]
    
    ECONOMIC_STATUS_CHOICES = [
        ('miskin', 'Miskin'),
        ('sangat_miskin', 'Sangat Miskin'),
        ('rentan_miskin', 'Rentan Miskin'),
        ('tidak_miskin', 'Tidak Miskin'),
    ]
    
    person = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='beneficiary_records')
    category = models.ForeignKey(BeneficiaryCategory, on_delete=models.CASCADE)
    registration_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    economic_status = models.CharField(max_length=20, choices=ECONOMIC_STATUS_CHOICES)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    family_members_count = models.PositiveIntegerField(default=1)
    house_condition = models.TextField(blank=True)
    special_needs = models.TextField(blank=True)
    verification_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='beneficiaries_registered')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.person.nama} - {self.category.name}'

    class Meta:
        verbose_name = 'Penerima Bantuan'
        verbose_name_plural = 'Penerima Bantuan'
        unique_together = ['person', 'category']


class Aid(models.Model):
    AID_TYPE_CHOICES = [
        ('uang', 'Bantuan Uang'),
        ('sembako', 'Sembako'),
        ('kesehatan', 'Bantuan Kesehatan'),
        ('pendidikan', 'Bantuan Pendidikan'),
        ('perumahan', 'Bantuan Perumahan'),
        ('usaha', 'Bantuan Usaha'),
        ('lainnya', 'Lainnya'),
    ]
    
    SOURCE_CHOICES = [
        ('pusat', 'Pemerintah Pusat'),
        ('provinsi', 'Pemerintah Provinsi'),
        ('kabupaten', 'Pemerintah Kabupaten'),
        ('desa', 'Pemerintah Desa'),
        ('swasta', 'Swasta'),
        ('lsm', 'LSM'),
        ('lainnya', 'Lainnya'),
    ]
    
    name = models.CharField(max_length=200)
    aid_type = models.CharField(max_length=20, choices=AID_TYPE_CHOICES)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    description = models.TextField(blank=True)
    value_per_beneficiary = models.DecimalField(max_digits=12, decimal_places=2)
    total_budget = models.DecimalField(max_digits=15, decimal_places=2)
    target_beneficiaries = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    requirements = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='beneficiaries_aid_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Bantuan'
        verbose_name_plural = 'Bantuan'


class AidDistribution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('approved', 'Disetujui'),
        ('distributed', 'Sudah Disalurkan'),
        ('rejected', 'Ditolak'),
    ]
    
    aid = models.ForeignKey(Aid, on_delete=models.CASCADE, related_name='distributions')
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='aid_received')
    distribution_date = models.DateField(null=True, blank=True)
    amount_received = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    receipt_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    distributed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.beneficiary.person.nama} - {self.aid.name}'

    class Meta:
        verbose_name = 'Distribusi Bantuan'
        verbose_name_plural = 'Distribusi Bantuan'
        unique_together = ['aid', 'beneficiary']


class BeneficiaryVerification(models.Model):
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Menunggu Verifikasi'),
        ('verified', 'Terverifikasi'),
        ('rejected', 'Ditolak'),
        ('need_update', 'Perlu Update Data'),
    ]
    
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='verifications')
    verification_date = models.DateField()
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES)
    verifier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    verification_notes = models.TextField(blank=True)
    documents_checked = models.TextField(blank=True)
    field_visit_conducted = models.BooleanField(default=False)
    field_visit_notes = models.TextField(blank=True)
    next_verification_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.beneficiary.person.nama} - {self.verification_date}'

    class Meta:
        verbose_name = 'Verifikasi Penerima Bantuan'
        verbose_name_plural = 'Verifikasi Penerima Bantuan'
        ordering = ['-verification_date']


class TarafKehidupan(models.Model):
    TARAF_CHOICES = [
        ('sangat_miskin', 'Sangat Miskin'),
        ('miskin', 'Miskin'),
        ('rentan_miskin', 'Rentan Miskin'),
        ('hampir_miskin', 'Hampir Miskin'),
        ('tidak_miskin', 'Tidak Miskin'),
    ]
    
    PENDIDIKAN_CHOICES = [
        ('tidak_sekolah', 'Tidak Sekolah'),
        ('sd', 'SD/Sederajat'),
        ('smp', 'SMP/Sederajat'),
        ('sma', 'SMA/Sederajat'),
        ('diploma', 'Diploma'),
        ('sarjana', 'Sarjana'),
        ('pascasarjana', 'Pascasarjana'),
    ]
    
    PEKERJAAN_CHOICES = [
        ('tidak_bekerja', 'Tidak Bekerja'),
        ('petani', 'Petani'),
        ('nelayan', 'Nelayan'),
        ('pedagang', 'Pedagang'),
        ('buruh', 'Buruh'),
        ('pns', 'PNS'),
        ('swasta', 'Karyawan Swasta'),
        ('wiraswasta', 'Wiraswasta'),
        ('lainnya', 'Lainnya'),
    ]
    
    KONDISI_RUMAH_CHOICES = [
        ('permanen', 'Permanen'),
        ('semi_permanen', 'Semi Permanen'),
        ('tidak_permanen', 'Tidak Permanen'),
    ]
    
    person = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='taraf_kehidupan')
    taraf_ekonomi = models.CharField(max_length=20, choices=TARAF_CHOICES)
    pendapatan_bulanan = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pendidikan_terakhir = models.CharField(max_length=20, choices=PENDIDIKAN_CHOICES)
    pekerjaan = models.CharField(max_length=20, choices=PEKERJAAN_CHOICES)
    jumlah_tanggungan = models.PositiveIntegerField(default=0)
    kondisi_rumah = models.CharField(max_length=20, choices=KONDISI_RUMAH_CHOICES)
    luas_rumah = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text='Dalam meter persegi')
    kepemilikan_rumah = models.CharField(max_length=50, default='milik_sendiri')
    sumber_air = models.CharField(max_length=100, blank=True)
    jenis_jamban = models.CharField(max_length=100, blank=True)
    sumber_penerangan = models.CharField(max_length=100, blank=True)
    bahan_bakar_memasak = models.CharField(max_length=100, blank=True)
    kepemilikan_aset = models.TextField(blank=True, help_text='Daftar aset yang dimiliki')
    catatan_khusus = models.TextField(blank=True)
    tanggal_survei = models.DateField()
    surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.person.nama} - {self.get_taraf_ekonomi_display()}'
    
    class Meta:
        verbose_name = 'Data Taraf Kehidupan'
        verbose_name_plural = 'Data Taraf Kehidupan'
        ordering = ['-tanggal_survei']


class DataBantuan(models.Model):
    JENIS_BANTUAN_CHOICES = [
        ('blt', 'Bantuan Langsung Tunai'),
        ('bpnt', 'Bantuan Pangan Non Tunai'),
        ('pkh', 'Program Keluarga Harapan'),
        ('pip', 'Program Indonesia Pintar'),
        ('kis', 'Kartu Indonesia Sehat'),
        ('bansos', 'Bantuan Sosial'),
        ('banpres', 'Bantuan Presiden'),
        ('banprov', 'Bantuan Provinsi'),
        ('bankab', 'Bantuan Kabupaten'),
        ('bangam', 'Bantuan Gampong'),
        ('lainnya', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('nonaktif', 'Non Aktif'),
        ('pending', 'Menunggu'),
        ('ditolak', 'Ditolak'),
        ('selesai', 'Selesai'),
    ]
    
    person = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='data_bantuan')
    jenis_bantuan = models.CharField(max_length=20, choices=JENIS_BANTUAN_CHOICES)
    nama_program = models.CharField(max_length=200)
    nomor_kartu = models.CharField(max_length=100, blank=True)
    nilai_bantuan = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    periode_bantuan = models.CharField(max_length=100, blank=True)
    tanggal_mulai = models.DateField()
    tanggal_berakhir = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    sumber_dana = models.CharField(max_length=100, blank=True)
    instansi_pemberi = models.CharField(max_length=200, blank=True)
    syarat_penerima = models.TextField(blank=True)
    dokumen_pendukung = models.TextField(blank=True)
    catatan = models.TextField(blank=True)
    input_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.person.nama} - {self.nama_program}'
    
    class Meta:
        verbose_name = 'Data Bantuan'
        verbose_name_plural = 'Data Bantuan'
        ordering = ['-tanggal_mulai']


def dokumen_upload_path(instance, filename):
    return f'dokumen_gampong/{instance.kategori}/{filename}'


class DokumenGampong(models.Model):
    KATEGORI_CHOICES = [
        ('administrasi', 'Administrasi'),
        ('keuangan', 'Keuangan'),
        ('pembangunan', 'Pembangunan'),
        ('sosial', 'Sosial'),
        ('kesehatan', 'Kesehatan'),
        ('pendidikan', 'Pendidikan'),
        ('keamanan', 'Keamanan'),
        ('lingkungan', 'Lingkungan'),
        ('ekonomi', 'Ekonomi'),
        ('budaya', 'Budaya'),
        ('lainnya', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('approved', 'Disetujui'),
        ('archived', 'Diarsipkan'),
    ]
    
    nama_dokumen = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES)
    deskripsi = models.TextField(blank=True)
    file_dokumen = models.FileField(upload_to=dokumen_upload_path)
    ukuran_file = models.PositiveIntegerField(null=True, blank=True, help_text='Ukuran file dalam bytes')
    tipe_file = models.CharField(max_length=50, blank=True)
    nomor_dokumen = models.CharField(max_length=100, blank=True)
    tanggal_dokumen = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    tags = models.CharField(max_length=500, blank=True, help_text='Pisahkan dengan koma')
    is_public = models.BooleanField(default=False, help_text='Dapat diakses publik')
    download_count = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_documents')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama_dokumen)
        
        if self.file_dokumen:
            self.ukuran_file = self.file_dokumen.size
            self.tipe_file = os.path.splitext(self.file_dokumen.name)[1].lower()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nama_dokumen
    
    def get_file_size_display(self):
        if self.ukuran_file:
            if self.ukuran_file < 1024:
                return f'{self.ukuran_file} B'
            elif self.ukuran_file < 1024 * 1024:
                return f'{self.ukuran_file / 1024:.1f} KB'
            else:
                return f'{self.ukuran_file / (1024 * 1024):.1f} MB'
        return 'Unknown'
    
    class Meta:
        verbose_name = 'Dokumen Gampong'
        verbose_name_plural = 'Dokumen Gampong'
        ordering = ['-created_at']


class Berita(models.Model):
    KATEGORI_CHOICES = [
        ('pengumuman', 'Pengumuman'),
        ('kegiatan', 'Kegiatan'),
        ('pembangunan', 'Pembangunan'),
        ('sosial', 'Sosial'),
        ('kesehatan', 'Kesehatan'),
        ('pendidikan', 'Pendidikan'),
        ('ekonomi', 'Ekonomi'),
        ('lainnya', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Dipublikasi'),
        ('archived', 'Diarsipkan'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    excerpt = models.TextField(blank=True, help_text='Ringkasan singkat berita')
    content = models.TextField()
    featured_image = models.ImageField(upload_to='berita/images/', null=True, blank=True)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    tags = models.CharField(max_length=500, blank=True, help_text='Pisahkan dengan koma')
    is_featured = models.BooleanField(default=False, help_text='Berita unggulan')
    allow_comments = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Berita'
        verbose_name_plural = 'Berita'
        ordering = ['-created_at']


class LetterTemplate(models.Model):
    nama = models.CharField(max_length=200)
    deskripsi = models.TextField(blank=True)
    content_template = models.TextField(help_text='Template konten surat dengan variabel [NAMA_VARIABEL]')
    variables = models.JSONField(default=list, help_text='Daftar variabel yang tersedia dalam template')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='beneficiaries_letter_template_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nama
    
    class Meta:
        verbose_name = 'Template Surat'
        verbose_name_plural = 'Template Surat'
        ordering = ['nama']


class Surat(models.Model):
    JENIS_CHOICES = [
        ('keterangan', 'Surat Keterangan'),
        ('pengantar', 'Surat Pengantar'),
        ('rekomendasi', 'Surat Rekomendasi'),
        ('undangan', 'Surat Undangan'),
        ('pemberitahuan', 'Surat Pemberitahuan'),
        ('permohonan', 'Surat Permohonan'),
        ('keputusan', 'Surat Keputusan'),
        ('lainnya', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Menunggu'),
        ('approved', 'Disetujui'),
        ('completed', 'Selesai'),
        ('rejected', 'Ditolak'),
    ]
    
    nomor_surat = models.CharField(max_length=100, unique=True)
    perihal = models.CharField(max_length=200)
    jenis = models.CharField(max_length=20, choices=JENIS_CHOICES)
    template = models.ForeignKey(LetterTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    penerima = models.CharField(max_length=200)
    alamat_penerima = models.TextField(blank=True)
    content = models.TextField(help_text='Konten surat yang sudah diisi')
    variables_data = models.JSONField(default=dict, help_text='Data variabel yang diisi')
    tanggal_surat = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    file_pdf = models.FileField(upload_to='surat/pdf/', null=True, blank=True)
    catatan = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='beneficiaries_surat_created')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='beneficiaries_approved_letters')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.nomor_surat} - {self.perihal}'
    
    class Meta:
        verbose_name = 'Surat'
        verbose_name_plural = 'Surat'
        ordering = ['-tanggal_surat']
