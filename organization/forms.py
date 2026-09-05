from django import forms
from .models import PerangkatDesa, LembagaAdat, PenggerakPKK, Kepemudaan, KarangTaruna
from references.models import Penduduk

class PerangkatDesaForm(forms.ModelForm):
    class Meta:
        model = PerangkatDesa
        fields = ['penduduk', 'jabatan', 'nip', 'sk_pengangkatan', 'tanggal_mulai_tugas', 
                 'tanggal_selesai_tugas', 'status', 'gaji_pokok', 'tunjangan', 'foto_profil', 
                 'deskripsi_tugas', 'kontak_whatsapp', 'email_dinas']
        widgets = {
            'penduduk': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'jabatan': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'nip': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'NIP'}),
            'sk_pengangkatan': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nomor SK Pengangkatan'}),
            'tanggal_mulai_tugas': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'tanggal_selesai_tugas': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'gaji_pokok': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Gaji Pokok'}),
            'tunjangan': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Tunjangan'}),
            'foto_profil': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'accept': 'image/*'}),
            'deskripsi_tugas': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Deskripsi Tugas'}),
            'kontak_whatsapp': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nomor WhatsApp'}),
            'email_dinas': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Email Dinas'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['penduduk'].required = True
        self.fields['jabatan'].required = True
        self.fields['tanggal_mulai_tugas'].required = True
        
    def clean(self):
        cleaned_data = super().clean()
        tanggal_mulai = cleaned_data.get('tanggal_mulai_tugas')
        tanggal_selesai = cleaned_data.get('tanggal_selesai_tugas')
        
        if tanggal_mulai and tanggal_selesai:
            if tanggal_selesai <= tanggal_mulai:
                raise forms.ValidationError('Tanggal selesai tugas harus setelah tanggal mulai tugas.')
        
        return cleaned_data

class LembagaAdatForm(forms.ModelForm):
    class Meta:
        model = LembagaAdat
        fields = ['nama_lembaga', 'jenis_lembaga', 'ketua', 'sekretaris', 'bendahara', 
                 'tanggal_terbentuk', 'alamat_sekretariat', 'deskripsi', 'kegiatan_rutin', 
                 'jumlah_anggota', 'status', 'kontak_phone', 'foto_kegiatan']
        widgets = {
            'nama_lembaga': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nama Lembaga'}),
            'jenis_lembaga': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'ketua': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'sekretaris': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'bendahara': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'tanggal_terbentuk': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'alamat_sekretariat': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Alamat Sekretariat'}),
            'deskripsi': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Deskripsi Lembaga'}),
            'kegiatan_rutin': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Kegiatan Rutin'}),
            'jumlah_anggota': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Jumlah Anggota'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'kontak_phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nomor Telepon'}),
            'foto_kegiatan': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'accept': 'image/*'}),
        }

class PenggerakPKKForm(forms.ModelForm):
    class Meta:
        model = PenggerakPKK
        fields = ['penduduk', 'jabatan', 'nomor_anggota', 'tanggal_bergabung', 'tanggal_keluar', 
                 'status', 'keahlian', 'pengalaman_organisasi', 'prestasi', 'foto_profil', 
                 'kontak_whatsapp', 'alamat_lengkap', 'email', 'deskripsi_tugas', 'sk_pengangkatan',
                 'tanggal_mulai_tugas', 'tanggal_selesai_tugas']
        widgets = {
            'penduduk': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'jabatan': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'nomor_anggota': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nomor Anggota'}),
            'tanggal_bergabung': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'tanggal_keluar': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'keahlian': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Keahlian yang dimiliki'}),
            'pengalaman_organisasi': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Pengalaman Organisasi'}),
            'prestasi': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Prestasi'}),
            'foto_profil': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'accept': 'image/*'}),
            'kontak_whatsapp': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nomor WhatsApp'}),
            'alamat_lengkap': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Alamat Lengkap'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Email'}),
            'deskripsi_tugas': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Deskripsi Tugas'}),
            'sk_pengangkatan': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nomor SK Pengangkatan'}),
            'tanggal_mulai_tugas': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'tanggal_selesai_tugas': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['penduduk'].required = True
        self.fields['jabatan'].required = True
        self.fields['tanggal_mulai_tugas'].required = True
        self.fields['status'].required = True

class KepemudaanForm(forms.ModelForm):
    # Tambahkan field yang tidak ada di model tapi ada di template
    wakil_ketua = forms.ModelChoiceField(
        queryset=Penduduk.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    jumlah_anggota = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Jumlah Anggota'})
    )
    tanggal_berdiri = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'})
    )
    sk_kepengurusan = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'SK Kepengurusan'})
    )
    lokasi_sekretariat = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Lokasi Sekretariat'})
    )
    kontak = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Kontak'})
    )
    foto_profil = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'accept': 'image/*'})
    )
    # Tambahkan field untuk media sosial
    media_sosial = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Media Sosial (Instagram/Facebook)'})
    )
    # Tambahkan field untuk visi misi
    visi_misi = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Visi dan Misi'})
    )
    
    class Meta:
        model = Kepemudaan
        fields = ['nama_organisasi', 'jenis_organisasi', 'ketua', 'sekretaris', 'bendahara', 
                 'tanggal_terbentuk', 'jumlah_anggota_aktif', 'rentang_usia', 
                 'kegiatan_rutin', 'prestasi', 'alamat_sekretariat', 'status', 
                 'kontak_phone', 'email', 'foto_kegiatan', 'deskripsi', 'media_sosial', 'visi_misi']
        widgets = {
            'nama_organisasi': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nama Organisasi'}),
            'jenis_organisasi': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'ketua': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'sekretaris': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'bendahara': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'tanggal_terbentuk': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'jumlah_anggota_aktif': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Jumlah Anggota Aktif'}),
            'rentang_usia': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Contoh: 15-30 tahun'}),
            'kegiatan_rutin': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Kegiatan Rutin'}),
            'prestasi': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Prestasi'}),
            'alamat_sekretariat': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Alamat Sekretariat'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'kontak_phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nomor Telepon'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Email'}),
            'foto_kegiatan': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'accept': 'image/*'}),
            'deskripsi': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Deskripsi'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['nama_organisasi'].required = True
        self.fields['jenis_organisasi'].required = True
        self.fields['ketua'].required = True
        self.fields['status'].required = True
        self.fields['tanggal_berdiri'].required = True
        
        # Jika instance sudah ada, isi field tambahan dengan data yang sesuai
        if self.instance and self.instance.pk:
            # Memetakan field dari model ke field form
            self.fields['tanggal_berdiri'].initial = self.instance.tanggal_terbentuk
            self.fields['jumlah_anggota'].initial = self.instance.jumlah_anggota_aktif
            self.fields['lokasi_sekretariat'].initial = self.instance.alamat_sekretariat
            self.fields['kontak'].initial = self.instance.kontak_phone
            self.fields['foto_profil'].initial = self.instance.foto_kegiatan
            
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Menyimpan data dari field tambahan ke field model yang sesuai
        # tanggal_berdiri wajib diisi dan disimpan ke tanggal_terbentuk
        instance.tanggal_terbentuk = self.cleaned_data.get('tanggal_berdiri')
        
        if self.cleaned_data.get('jumlah_anggota'):
            instance.jumlah_anggota_aktif = self.cleaned_data.get('jumlah_anggota')
        if self.cleaned_data.get('lokasi_sekretariat'):
            instance.alamat_sekretariat = self.cleaned_data.get('lokasi_sekretariat')
        if self.cleaned_data.get('kontak'):
            instance.kontak_phone = self.cleaned_data.get('kontak')
        if self.cleaned_data.get('foto_profil'):
            instance.foto_kegiatan = self.cleaned_data.get('foto_profil')
        if self.cleaned_data.get('media_sosial'):
            instance.media_sosial = self.cleaned_data.get('media_sosial')
        if self.cleaned_data.get('visi_misi'):
            instance.visi_misi = self.cleaned_data.get('visi_misi')
            
        if commit:
            instance.save()
        return instance

class KarangTarunaForm(forms.ModelForm):
    class Meta:
        model = KarangTaruna
        fields = ['penduduk', 'jabatan', 'nomor_anggota', 'tanggal_bergabung', 'tanggal_keluar', 
                 'status', 'bidang_keahlian', 'pengalaman_organisasi', 'prestasi_individu', 
                 'kontribusi', 'foto_profil', 'kontak_whatsapp', 'email_pribadi', 'alamat_lengkap', 
                 'pendidikan_terakhir', 'pekerjaan', 'is_pengurus_inti']
        widgets = {
            'penduduk': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'jabatan': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'nomor_anggota': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nomor Anggota'}),
            'tanggal_bergabung': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'tanggal_keluar': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'bidang_keahlian': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Bidang Keahlian'}),
            'pengalaman_organisasi': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Pengalaman Organisasi'}),
            'prestasi_individu': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Prestasi Individu'}),
            'kontribusi': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Kontribusi'}),
            'foto_profil': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'accept': 'image/*'}),
            'kontak_whatsapp': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nomor WhatsApp'}),
            'email_pribadi': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Email Pribadi'}),
            'alamat_lengkap': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3, 'placeholder': 'Alamat Lengkap'}),
            'pendidikan_terakhir': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Pendidikan Terakhir'}),
            'pekerjaan': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Pekerjaan'}),
            'is_pengurus_inti': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50'}),
        }