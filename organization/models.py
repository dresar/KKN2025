from django.db import models
from django.contrib.auth.models import User
from references.models import Penduduk


# Model untuk Data Perangkat Desa
class PerangkatDesa(models.Model):
    JABATAN_CHOICES = [
        ('kepala_desa', 'Kepala Desa'),
        ('sekretaris_desa', 'Sekretaris Desa'),
        ('kaur_pemerintahan', 'Kaur Pemerintahan'),
        ('kaur_pembangunan', 'Kaur Pembangunan'),
        ('kaur_kesra', 'Kaur Kesejahteraan Rakyat'),
        ('kaur_keuangan', 'Kaur Keuangan'),
        ('kaur_umum', 'Kaur Umum'),
        ('kasi_pemerintahan', 'Kasi Pemerintahan'),
        ('kasi_pembangunan', 'Kasi Pembangunan'),
        ('kasi_kesra', 'Kasi Kesejahteraan Rakyat'),
        ('kepala_dusun', 'Kepala Dusun'),
        ('staf', 'Staf'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('non_aktif', 'Non Aktif'),
        ('pensiun', 'Pensiun'),
    ]
    
    penduduk = models.ForeignKey(Penduduk, on_delete=models.CASCADE)
    jabatan = models.CharField(max_length=50, choices=JABATAN_CHOICES)
    nip = models.CharField(max_length=50, blank=True, null=True)
    sk_pengangkatan = models.CharField(max_length=100, blank=True)
    tanggal_mulai_tugas = models.DateField()
    tanggal_selesai_tugas = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    gaji_pokok = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    tunjangan = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    foto_profil = models.ImageField(upload_to='organization/perangkat/', blank=True, null=True)
    deskripsi_tugas = models.TextField(blank=True)
    kontak_whatsapp = models.CharField(max_length=20, blank=True)
    email_dinas = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perangkat Desa"
        verbose_name_plural = "Data Perangkat Desa"
        unique_together = ('penduduk', 'jabatan')
        ordering = ['jabatan', 'penduduk__name']
        indexes = [
            models.Index(fields=['jabatan']),
            models.Index(fields=['status']),
            models.Index(fields=['nip']),
            models.Index(fields=['jabatan', 'status']),
            models.Index(fields=['status', 'tanggal_mulai_tugas']),
        ]
    
    def __str__(self):
        return f"{self.penduduk.name} - {self.get_jabatan_display()}"


# Model untuk Data Lembaga Adat
class LembagaAdat(models.Model):
    JENIS_LEMBAGA_CHOICES = [
        ('adat_istiadat', 'Lembaga Adat Istiadat'),
        ('keagamaan', 'Lembaga Keagamaan'),
        ('budaya', 'Lembaga Budaya'),
        ('tradisi', 'Lembaga Tradisi'),
        ('ritual', 'Lembaga Ritual'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('non_aktif', 'Non Aktif'),
        ('dalam_pembinaan', 'Dalam Pembinaan'),
    ]
    
    nama_lembaga = models.CharField(max_length=200)
    jenis_lembaga = models.CharField(max_length=50, choices=JENIS_LEMBAGA_CHOICES)
    ketua = models.ForeignKey(Penduduk, on_delete=models.SET_NULL, null=True, related_name='ketua_lembaga_adat')
    sekretaris = models.ForeignKey(Penduduk, on_delete=models.SET_NULL, null=True, blank=True, related_name='sekretaris_lembaga_adat')
    bendahara = models.ForeignKey(Penduduk, on_delete=models.SET_NULL, null=True, blank=True, related_name='bendahara_lembaga_adat')
    tanggal_terbentuk = models.DateField()
    alamat_sekretariat = models.TextField(blank=True)
    deskripsi = models.TextField(blank=True)
    kegiatan_rutin = models.TextField(blank=True, help_text="Daftar kegiatan rutin yang dilakukan")
    jumlah_anggota = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    kontak_phone = models.CharField(max_length=20, blank=True)
    foto_kegiatan = models.ImageField(upload_to='organization/lembaga_adat/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Lembaga Adat"
        verbose_name_plural = "Data Lembaga Adat"
        ordering = ['nama_lembaga']
        indexes = [
            models.Index(fields=['nama_lembaga']),
            models.Index(fields=['jenis_lembaga']),
            models.Index(fields=['status']),
            models.Index(fields=['jenis_lembaga', 'status']),
            models.Index(fields=['status', 'tanggal_terbentuk']),
        ]
    
    def __str__(self):
        return self.nama_lembaga


# Model untuk Data Penggerak PKK
class PenggerakPKK(models.Model):
    JABATAN_PKK_CHOICES = [
        ('ketua_tim_penggerak', 'Ketua Tim Penggerak PKK'),
        ('wakil_ketua', 'Wakil Ketua'),
        ('sekretaris', 'Sekretaris'),
        ('bendahara', 'Bendahara'),
        ('pokja_1', 'Pokja I (Penghayatan dan Pengamalan Pancasila)'),
        ('pokja_2', 'Pokja II (Gotong Royong)'),
        ('pokja_3', 'Pokja III (Pangan, Sandang, Papan)'),
        ('pokja_4', 'Pokja IV (Pendidikan dan Keterampilan)'),
        ('anggota', 'Anggota'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('non_aktif', 'Non Aktif'),
        ('cuti', 'Cuti'),
    ]
    
    penduduk = models.ForeignKey(Penduduk, on_delete=models.CASCADE)
    jabatan = models.CharField(max_length=50, choices=JABATAN_PKK_CHOICES)
    nomor_anggota = models.CharField(max_length=50, blank=True)
    tanggal_bergabung = models.DateField()
    tanggal_keluar = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    keahlian = models.TextField(blank=True, help_text="Keahlian yang dimiliki")
    pengalaman_organisasi = models.TextField(blank=True)
    prestasi = models.TextField(blank=True)
    foto_profil = models.ImageField(upload_to='organization/pkk/', blank=True, null=True)
    kontak_whatsapp = models.CharField(max_length=20, blank=True)
    alamat_lengkap = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    deskripsi_tugas = models.TextField(blank=True)
    sk_pengangkatan = models.CharField(max_length=100, blank=True)
    tanggal_mulai_tugas = models.DateField(blank=True, null=True)
    tanggal_selesai_tugas = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Penggerak PKK"
        verbose_name_plural = "Data Penggerak PKK"
        unique_together = ('penduduk', 'jabatan')
        ordering = ['jabatan', 'penduduk__name']
        indexes = [
            models.Index(fields=['jabatan']),
            models.Index(fields=['status']),
            models.Index(fields=['nomor_anggota']),
            models.Index(fields=['jabatan', 'status']),
            models.Index(fields=['status', 'tanggal_bergabung']),
        ]
    
    def __str__(self):
        return f"{self.penduduk.name} - {self.get_jabatan_display()}"


# Model untuk Data Kepemudaan
class Kepemudaan(models.Model):
    JENIS_ORGANISASI_CHOICES = [
        ('karang_taruna', 'Karang Taruna'),
        ('remaja_masjid', 'Remaja Masjid'),
        ('pramuka', 'Pramuka'),
        ('olahraga', 'Organisasi Olahraga'),
        ('seni_budaya', 'Seni dan Budaya'),
        ('kewirausahaan', 'Kewirausahaan Muda'),
        ('lainnya', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('non_aktif', 'Non Aktif'),
        ('alumni', 'Alumni'),
    ]
    
    nama_organisasi = models.CharField(max_length=200)
    jenis_organisasi = models.CharField(max_length=50, choices=JENIS_ORGANISASI_CHOICES)
    ketua = models.ForeignKey(Penduduk, on_delete=models.SET_NULL, null=True, related_name='ketua_kepemudaan')
    sekretaris = models.ForeignKey(Penduduk, on_delete=models.SET_NULL, null=True, blank=True, related_name='sekretaris_kepemudaan')
    bendahara = models.ForeignKey(Penduduk, on_delete=models.SET_NULL, null=True, blank=True, related_name='bendahara_kepemudaan')
    tanggal_terbentuk = models.DateField()
    jumlah_anggota_aktif = models.PositiveIntegerField(default=0)
    rentang_usia = models.CharField(max_length=50, blank=True, help_text="Contoh: 15-30 tahun")
    kegiatan_rutin = models.TextField(blank=True)
    prestasi = models.TextField(blank=True)
    alamat_sekretariat = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    kontak_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    foto_kegiatan = models.ImageField(upload_to='organization/kepemudaan/', blank=True, null=True)
    deskripsi = models.TextField(blank=True)
    media_sosial = models.CharField(max_length=200, blank=True, help_text="Media sosial organisasi (Instagram/Facebook)")
    visi_misi = models.TextField(blank=True, help_text="Visi dan misi organisasi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Organisasi Kepemudaan"
        verbose_name_plural = "Data Kepemudaan"
        ordering = ['nama_organisasi']
        indexes = [
            models.Index(fields=['nama_organisasi']),
            models.Index(fields=['jenis_organisasi']),
            models.Index(fields=['status']),
            models.Index(fields=['jenis_organisasi', 'status']),
            models.Index(fields=['status', 'tanggal_terbentuk']),
        ]
    
    def __str__(self):
        return self.nama_organisasi


# Model untuk Data Karang Taruna (Detail khusus)
class KarangTaruna(models.Model):
    JABATAN_CHOICES = [
        ('ketua_umum', 'Ketua Umum'),
        ('wakil_ketua', 'Wakil Ketua'),
        ('sekretaris_umum', 'Sekretaris Umum'),
        ('wakil_sekretaris', 'Wakil Sekretaris'),
        ('bendahara_umum', 'Bendahara Umum'),
        ('wakil_bendahara', 'Wakil Bendahara'),
        ('koordinator_bidang_1', 'Koordinator Bidang Pendidikan dan Pelatihan'),
        ('koordinator_bidang_2', 'Koordinator Bidang Olahraga dan Seni'),
        ('koordinator_bidang_3', 'Koordinator Bidang Kewirausahaan'),
        ('koordinator_bidang_4', 'Koordinator Bidang Lingkungan Hidup'),
        ('koordinator_bidang_5', 'Koordinator Bidang Keagamaan dan Sosial'),
        ('anggota_aktif', 'Anggota Aktif'),
        ('anggota_biasa', 'Anggota Biasa'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('non_aktif', 'Non Aktif'),
        ('alumni', 'Alumni'),
        ('calon_anggota', 'Calon Anggota'),
    ]
    
    penduduk = models.ForeignKey(Penduduk, on_delete=models.CASCADE)
    nomor_anggota = models.CharField(max_length=50, unique=True)
    jabatan = models.CharField(max_length=50, choices=JABATAN_CHOICES)
    tanggal_bergabung = models.DateField()
    tanggal_keluar = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    bidang_keahlian = models.TextField(blank=True, help_text="Bidang keahlian atau minat")
    pengalaman_organisasi = models.TextField(blank=True)
    prestasi_individu = models.TextField(blank=True)
    kontribusi = models.TextField(blank=True, help_text="Kontribusi terhadap organisasi")
    foto_profil = models.ImageField(upload_to='organization/karang_taruna/', blank=True, null=True)
    kontak_whatsapp = models.CharField(max_length=20, blank=True)
    email_pribadi = models.EmailField(blank=True)
    alamat_lengkap = models.TextField(blank=True)
    pendidikan_terakhir = models.CharField(max_length=100, blank=True)
    pekerjaan = models.CharField(max_length=100, blank=True)
    is_pengurus_inti = models.BooleanField(default=False, help_text="Apakah termasuk pengurus inti")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Anggota Karang Taruna"
        verbose_name_plural = "Data Karang Taruna"
        unique_together = ('penduduk', 'jabatan')
        ordering = ['jabatan', 'penduduk__name']
        indexes = [
            models.Index(fields=['jabatan']),
            models.Index(fields=['status']),
            models.Index(fields=['nomor_anggota']),
            models.Index(fields=['is_pengurus_inti']),
            models.Index(fields=['jabatan', 'status']),
            models.Index(fields=['status', 'is_pengurus_inti']),
            models.Index(fields=['status', 'tanggal_bergabung']),
        ]
    
    def __str__(self):
        return f"{self.penduduk.name} - {self.get_jabatan_display()} ({self.nomor_anggota})"