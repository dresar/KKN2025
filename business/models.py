from django.db import models
from django.contrib.auth import get_user_model
from references.models import Penduduk

User = get_user_model()


class BusinessCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Kategori Bisnis'
        verbose_name_plural = 'Kategori Bisnis'


class Business(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('umkm', 'UMKM'),
        ('koperasi', 'Koperasi'),
        ('bumg', 'BUMG'),
        ('toko', 'Toko'),
        ('warung', 'Warung'),
        ('jasa', 'Jasa'),
        ('lainnya', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
        ('tutup', 'Tutup'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.ForeignKey(BusinessCategory, on_delete=models.CASCADE)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES)
    description = models.TextField(blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    established_date = models.DateField(null=True, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    employee_count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Bisnis'
        verbose_name_plural = 'Bisnis'


class BusinessOwner(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='owners')
    owner = models.ForeignKey(Penduduk, on_delete=models.CASCADE)
    ownership_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    role = models.CharField(max_length=100, default='Pemilik')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.owner.nama} - {self.business.name} ({self.ownership_percentage}%)'

    class Meta:
        verbose_name = 'Pemilik Bisnis'
        verbose_name_plural = 'Pemilik Bisnis'
        unique_together = ['business', 'owner']


class BusinessProduct(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=50, default='pcs')
    stock_quantity = models.PositiveIntegerField(default=0)
    min_stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='business_products/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.business.name}'

    class Meta:
        verbose_name = 'Produk Bisnis'
        verbose_name_plural = 'Produk Bisnis'


class BusinessFinance(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Pemasukan'),
        ('expense', 'Pengeluaran'),
        ('investment', 'Investasi'),
        ('loan', 'Pinjaman'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='finances')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    transaction_date = models.DateField()
    category = models.CharField(max_length=100, blank=True)
    receipt_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.business.name} - {self.get_transaction_type_display()} - Rp {self.amount:,.0f}'

    class Meta:
        verbose_name = 'Keuangan Bisnis'
        verbose_name_plural = 'Keuangan Bisnis'
        ordering = ['-transaction_date']


class JenisKoperasi(models.Model):
    nama = models.CharField(max_length=100, unique=True)
    deskripsi = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nama
    
    class Meta:
        verbose_name = 'Jenis Koperasi'
        verbose_name_plural = 'Jenis Koperasi'
        ordering = ['nama']


class Koperasi(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
        ('pending', 'Pending'),
    ]
    
    nama = models.CharField(max_length=200)
    nomor_badan_hukum = models.CharField(max_length=100, unique=True)
    tanggal_berdiri = models.DateField()
    alamat = models.TextField()
    ketua = models.CharField(max_length=100)
    sekretaris = models.CharField(max_length=100)
    bendahara = models.CharField(max_length=100)
    jumlah_anggota = models.PositiveIntegerField(default=0)
    modal_awal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    modal_sekarang = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    jenis_koperasi = models.ForeignKey(JenisKoperasi, on_delete=models.SET_NULL, null=True, blank=True)
    jenis_usaha = models.TextField()
    telepon = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nama
    
    class Meta:
        verbose_name = 'Koperasi'
        verbose_name_plural = 'Koperasi'


class BUMG(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
        ('pending', 'Pending'),
    ]
    
    nama = models.CharField(max_length=200)
    nomor_sk = models.CharField(max_length=100, unique=True)
    tanggal_sk = models.DateField()
    alamat = models.TextField()
    direktur = models.CharField(max_length=100)
    komisaris = models.CharField(max_length=100)
    modal_dasar = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    modal_disetor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    bidang_usaha = models.TextField()
    telepon = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nama
    
    class Meta:
        verbose_name = 'BUMG'
        verbose_name_plural = 'BUMG'


class UKM(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
        ('pending', 'Pending'),
    ]
    
    SKALA_CHOICES = [
        ('mikro', 'Mikro'),
        ('kecil', 'Kecil'),
        ('menengah', 'Menengah'),
    ]
    
    nama_usaha = models.CharField(max_length=200)
    pemilik = models.CharField(max_length=100)
    nik_pemilik = models.CharField(max_length=16)
    alamat_usaha = models.TextField()
    alamat_pemilik = models.TextField()
    jenis_usaha = models.CharField(max_length=100)
    skala_usaha = models.CharField(max_length=20, choices=SKALA_CHOICES)
    modal_awal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    omzet_bulanan = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    jumlah_karyawan = models.PositiveIntegerField(default=1)
    tanggal_mulai = models.DateField()
    nomor_izin = models.CharField(max_length=100, blank=True)
    telepon = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    produk_utama = models.TextField()
    target_pasar = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nama_usaha
    
    class Meta:
        verbose_name = 'UKM'
        verbose_name_plural = 'UKM'


class Aset(models.Model):
    KATEGORI_CHOICES = [
        ('tanah', 'Tanah'),
        ('bangunan', 'Bangunan'),
        ('kendaraan', 'Kendaraan'),
        ('peralatan', 'Peralatan'),
        ('inventaris', 'Inventaris'),
        ('lainnya', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('baik', 'Baik'),
        ('rusak_ringan', 'Rusak Ringan'),
        ('rusak_berat', 'Rusak Berat'),
        ('hilang', 'Hilang'),
    ]
    
    nama_aset = models.CharField(max_length=200)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES)
    kode_aset = models.CharField(max_length=50, unique=True)
    deskripsi = models.TextField()
    lokasi = models.CharField(max_length=200)
    nilai_perolehan = models.DecimalField(max_digits=15, decimal_places=2)
    tanggal_perolehan = models.DateField()
    kondisi = models.CharField(max_length=20, choices=STATUS_CHOICES, default='baik')
    masa_manfaat = models.PositiveIntegerField(help_text='Dalam tahun')
    penyusutan_per_tahun = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    nilai_buku = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    penanggung_jawab = models.CharField(max_length=100)
    nomor_sertifikat = models.CharField(max_length=100, blank=True)
    foto = models.ImageField(upload_to='aset_photos/', null=True, blank=True)
    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.nama_aset} ({self.kode_aset})'
    
    class Meta:
        verbose_name = 'Aset'
        verbose_name_plural = 'Aset'


class LayananJasa(models.Model):
    KATEGORI_CHOICES = [
        ('kesehatan', 'Kesehatan'),
        ('pendidikan', 'Pendidikan'),
        ('transportasi', 'Transportasi'),
        ('konstruksi', 'Konstruksi'),
        ('teknologi', 'Teknologi'),
        ('keuangan', 'Keuangan'),
        ('pertanian', 'Pertanian'),
        ('lainnya', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
        ('pending', 'Pending'),
    ]
    
    SATUAN_HARGA_CHOICES = [
        ('per_jam', 'Per Jam'),
        ('per_hari', 'Per Hari'),
        ('per_minggu', 'Per Minggu'),
        ('per_bulan', 'Per Bulan'),
        ('per_proyek', 'Per Proyek'),
        ('lainnya', 'Lainnya'),
    ]
    
    nama = models.CharField(max_length=200)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES)
    deskripsi = models.TextField()
    penyedia = models.CharField(max_length=100)
    telepon = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    alamat = models.TextField()
    pengalaman = models.PositiveIntegerField(default=0, help_text='Dalam tahun')
    harga_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    harga_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    satuan_harga = models.CharField(max_length=20, choices=SATUAN_HARGA_CHOICES, default='per_proyek')
    waktu_layanan = models.CharField(max_length=200, blank=True)
    area_layanan = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    website = models.URLField(blank=True)
    sertifikat = models.CharField(max_length=200, blank=True)
    keunggulan = models.TextField(blank=True)
    syarat_ketentuan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nama
    
    class Meta:
        verbose_name = 'Layanan Jasa'
        verbose_name_plural = 'Layanan Jasa'
