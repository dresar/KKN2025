from django.db import models
from django.contrib.auth import get_user_model
from references.models import Penduduk
from django.utils import timezone
from datetime import date

User = get_user_model()


class PosyanduLocation(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    coordinator = models.ForeignKey(Penduduk, on_delete=models.SET_NULL, null=True, blank=True, related_name='coordinated_posyandu')
    contact_phone = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=50)
    facilities = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    established_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Lokasi Posyandu'
        verbose_name_plural = 'Lokasi Posyandu'


class PosyanduSchedule(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('pemeriksaan', 'Pemeriksaan Rutin'),
        ('imunisasi', 'Imunisasi'),
        ('penyuluhan', 'Penyuluhan'),
        ('penimbangan', 'Penimbangan'),
        ('vitamin', 'Pemberian Vitamin'),
        ('lainnya', 'Lainnya'),
    ]
    
    location = models.ForeignKey(PosyanduLocation, on_delete=models.CASCADE, related_name='schedules')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    schedule_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    target_participants = models.PositiveIntegerField(default=0)
    actual_participants = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posyandu_location_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} - {self.location.name} ({self.schedule_date})'

    class Meta:
        verbose_name = 'Jadwal Posyandu'
        verbose_name_plural = 'Jadwal Posyandu'
        ordering = ['-schedule_date', 'start_time']


class HealthRecord(models.Model):
    PATIENT_TYPE_CHOICES = [
        ('balita', 'Balita'),
        ('ibu_hamil', 'Ibu Hamil'),
        ('ibu_menyusui', 'Ibu Menyusui'),
        ('lansia', 'Lansia'),
    ]
    
    patient = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='health_records')
    posyandu = models.ForeignKey(PosyanduLocation, on_delete=models.CASCADE)
    patient_type = models.CharField(max_length=20, choices=PATIENT_TYPE_CHOICES)
    visit_date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    complaints = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    next_visit = models.DateField(null=True, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.patient.name} - {self.visit_date}'

    class Meta:
        verbose_name = 'Rekam Kesehatan'
        verbose_name_plural = 'Rekam Kesehatan'
        ordering = ['-visit_date']


class Immunization(models.Model):
    VACCINE_TYPE_CHOICES = [
        ('bcg', 'BCG'),
        ('hepatitis_b', 'Hepatitis B'),
        ('polio', 'Polio'),
        ('dpt', 'DPT'),
        ('campak', 'Campak'),
        ('mmr', 'MMR'),
        ('covid19', 'COVID-19'),
        ('lainnya', 'Lainnya'),
    ]
    
    patient = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='immunizations')
    posyandu = models.ForeignKey(PosyanduLocation, on_delete=models.CASCADE)
    vaccine_type = models.CharField(max_length=20, choices=VACCINE_TYPE_CHOICES)
    vaccine_name = models.CharField(max_length=100)
    dose_number = models.PositiveIntegerField(default=1)
    immunization_date = models.DateField()
    batch_number = models.CharField(max_length=50, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    side_effects = models.TextField(blank=True)
    next_dose_date = models.DateField(null=True, blank=True)
    administered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.patient.name} - {self.vaccine_name} (Dosis {self.dose_number})'

    class Meta:
        verbose_name = 'Imunisasi'
        verbose_name_plural = 'Imunisasi'
        ordering = ['-immunization_date']


class NutritionData(models.Model):
    NUTRITION_STATUS_CHOICES = [
        ('normal', 'Normal'),
        ('kurang', 'Kurang Gizi'),
        ('buruk', 'Gizi Buruk'),
        ('lebih', 'Gizi Lebih'),
        ('stunting', 'Stunting'),
        ('wasting', 'Wasting'),
    ]
    
    patient = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='nutrition_data')
    posyandu = models.ForeignKey(PosyanduLocation, on_delete=models.CASCADE)
    measurement_date = models.DateField()
    age_months = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    head_circumference = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    arm_circumference = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    nutrition_status = models.CharField(max_length=20, choices=NUTRITION_STATUS_CHOICES)
    vitamin_a_given = models.BooleanField(default=False)
    iron_supplement_given = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.patient.name} - {self.measurement_date} ({self.nutrition_status})'

    class Meta:
        verbose_name = 'Data Nutrisi'
        verbose_name_plural = 'Data Nutrisi'
        ordering = ['-measurement_date']


class PosyanduKader(models.Model):
    JABATAN_CHOICES = [
        ('ketua', 'Ketua'),
        ('wakil_ketua', 'Wakil Ketua'),
        ('sekretaris', 'Sekretaris'),
        ('bendahara', 'Bendahara'),
        ('anggota', 'Anggota'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('nonaktif', 'Non-Aktif'),
        ('cuti', 'Cuti'),
    ]
    
    penduduk = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='kader_posyandu')
    posyandu = models.ForeignKey(PosyanduLocation, on_delete=models.CASCADE, related_name='kader')
    jabatan = models.CharField(max_length=20, choices=JABATAN_CHOICES)
    nomor_hp = models.CharField(max_length=15, blank=True)
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='aktif')
    sertifikat = models.FileField(upload_to='kader_sertifikat/', blank=True, null=True)
    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.penduduk.name} - {self.posyandu.name} ({self.jabatan})'
    
    class Meta:
        verbose_name = 'Kader Posyandu'
        verbose_name_plural = 'Kader Posyandu'
        unique_together = ['penduduk', 'posyandu', 'jabatan']
        ordering = ['-created_at']


class IbuHamil(models.Model):
    RIWAYAT_KEHAMILAN_CHOICES = [
        ('1', 'Kehamilan Pertama'),
        ('2', 'Kehamilan Kedua'),
        ('3', 'Kehamilan Ketiga'),
        ('4+', 'Kehamilan Keempat atau Lebih'),
    ]
    
    RISIKO_CHOICES = [
        ('rendah', 'Risiko Rendah'),
        ('tinggi', 'Risiko Tinggi'),
    ]
    
    penduduk = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='kehamilan')
    posyandu = models.ForeignKey(PosyanduLocation, on_delete=models.CASCADE)
    tanggal_hpht = models.DateField(help_text='Hari Pertama Haid Terakhir')
    usia_kehamilan = models.PositiveIntegerField(help_text='Dalam minggu')
    tanggal_perkiraan_lahir = models.DateField()
    riwayat_kehamilan = models.CharField(max_length=5, choices=RIWAYAT_KEHAMILAN_CHOICES)
    berat_badan_sebelum_hamil = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tinggi_badan = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    golongan_darah = models.CharField(max_length=5, blank=True)
    riwayat_penyakit = models.TextField(blank=True)
    risiko_kehamilan = models.CharField(max_length=10, choices=RISIKO_CHOICES, default='rendah')
    nomor_buku_kia = models.CharField(max_length=50, blank=True)
    status_aktif = models.BooleanField(default=True)
    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.tanggal_hpht and not self.tanggal_perkiraan_lahir:
            from datetime import timedelta
            self.tanggal_perkiraan_lahir = self.tanggal_hpht + timedelta(days=280)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.penduduk.name} - Hamil {self.usia_kehamilan} minggu'
    
    class Meta:
        verbose_name = 'Ibu Hamil'
        verbose_name_plural = 'Ibu Hamil'
        ordering = ['-created_at']


class PemeriksaanIbuHamil(models.Model):
    ibu_hamil = models.ForeignKey(IbuHamil, on_delete=models.CASCADE, related_name='pemeriksaan')
    tanggal_periksa = models.DateField()
    usia_kehamilan = models.PositiveIntegerField(help_text='Dalam minggu')
    berat_badan = models.DecimalField(max_digits=5, decimal_places=2)
    tekanan_darah = models.CharField(max_length=20)
    tinggi_fundus = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    lingkar_lengan_atas = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    hemoglobin = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    protein_urin = models.CharField(max_length=10, blank=True)
    tablet_fe = models.BooleanField(default=False)
    imunisasi_tt = models.BooleanField(default=False)
    keluhan = models.TextField(blank=True)
    anjuran = models.TextField(blank=True)
    pemeriksa = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.ibu_hamil.penduduk.name} - {self.tanggal_periksa}'
    
    class Meta:
        verbose_name = 'Pemeriksaan Ibu Hamil'
        verbose_name_plural = 'Pemeriksaan Ibu Hamil'
        ordering = ['-tanggal_periksa']


class StuntingData(models.Model):
    STATUS_STUNTING_CHOICES = [
        ('normal', 'Normal'),
        ('pendek', 'Pendek (Stunted)'),
        ('sangat_pendek', 'Sangat Pendek (Severely Stunted)'),
    ]
    
    INTERVENSI_CHOICES = [
        ('gizi', 'Intervensi Gizi'),
        ('kesehatan', 'Intervensi Kesehatan'),
        ('sanitasi', 'Intervensi Sanitasi'),
        ('edukasi', 'Edukasi Keluarga'),
    ]
    
    balita = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='stunting_data')
    posyandu = models.ForeignKey(PosyanduLocation, on_delete=models.CASCADE)
    tanggal_ukur = models.DateField()
    usia_bulan = models.PositiveIntegerField()
    tinggi_badan = models.DecimalField(max_digits=5, decimal_places=2)
    berat_badan = models.DecimalField(max_digits=5, decimal_places=2)
    z_score_tb_u = models.DecimalField(max_digits=5, decimal_places=2, help_text='Z-Score Tinggi Badan menurut Umur')
    z_score_bb_u = models.DecimalField(max_digits=5, decimal_places=2, help_text='Z-Score Berat Badan menurut Umur', null=True, blank=True)
    z_score_bb_tb = models.DecimalField(max_digits=5, decimal_places=2, help_text='Z-Score Berat Badan menurut Tinggi Badan', null=True, blank=True)
    status_stunting = models.CharField(max_length=15, choices=STATUS_STUNTING_CHOICES)
    asi_eksklusif = models.BooleanField(default=False)
    riwayat_bblr = models.BooleanField(default=False, help_text='Berat Badan Lahir Rendah')
    riwayat_penyakit = models.TextField(blank=True)
    intervensi_diberikan = models.CharField(max_length=20, choices=INTERVENSI_CHOICES, blank=True)
    hasil_intervensi = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    keterangan = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.balita.name} - {self.tanggal_ukur} ({self.status_stunting})'
    
    class Meta:
        verbose_name = 'Data Stunting'
        verbose_name_plural = 'Data Stunting'
        ordering = ['-tanggal_ukur']
