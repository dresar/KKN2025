from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import VillageHistory, VillageHistoryPhoto


class VillageHistoryForm(forms.ModelForm):
    """Form untuk Sejarah Desa"""
    
    class Meta:
        model = VillageHistory
        fields = [
            'title', 'slug', 'summary', 'content', 'history_type',
            'year_start', 'year_end', 'period_start', 'period_end',
            'featured_image', 'source', 'author', 'is_featured', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Masukkan judul sejarah...'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'URL slug (otomatis dari judul)'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Ringkasan singkat sejarah...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 10,
                'placeholder': 'Isi lengkap sejarah desa...'
            }),
            'history_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'year_start': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Tahun mulai (contoh: 1945)'
            }),
            'year_end': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Tahun berakhir (opsional)'
            }),
            'period_start': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'period_end': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'featured_image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'source': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Sumber informasi...'
            }),
            'author': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nama penulis/peneliti...'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
        labels = {
            'title': 'Judul Sejarah',
            'slug': 'URL Slug',
            'summary': 'Ringkasan',
            'content': 'Isi Sejarah',
            'history_type': 'Jenis Sejarah',
            'year_start': 'Tahun Mulai',
            'year_end': 'Tahun Berakhir',
            'period_start': 'Periode Mulai',
            'period_end': 'Periode Berakhir',
            'featured_image': 'Gambar Utama',
            'source': 'Sumber',
            'author': 'Penulis',
            'is_featured': 'Tampilkan di Beranda',
            'is_active': 'Status Aktif'
        }
        help_texts = {
            'slug': 'URL slug akan dibuat otomatis dari judul jika dikosongkan',
            'summary': 'Ringkasan singkat yang akan ditampilkan di daftar sejarah',
            'history_type': 'Pilih jenis/kategori sejarah',
            'year_start': 'Tahun dimulainya peristiwa sejarah',
            'year_end': 'Tahun berakhirnya peristiwa (opsional)',
            'period_start': 'Tanggal mulai periode (opsional)',
            'period_end': 'Tanggal akhir periode (opsional)',
            'source': 'Sumber referensi informasi sejarah',
            'author': 'Nama penulis atau peneliti',
            'is_featured': 'Centang untuk menampilkan di halaman utama',
            'is_active': 'Centang untuk mengaktifkan sejarah ini'
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError('Judul sejarah harus diisi.')
        if len(title) < 5:
            raise ValidationError('Judul sejarah minimal 5 karakter.')
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise ValidationError('Isi sejarah harus diisi.')
        if len(content) < 50:
            raise ValidationError('Isi sejarah minimal 50 karakter.')
        return content
    
    def clean_year_start(self):
        year_start = self.cleaned_data.get('year_start')
        if year_start:
            current_year = timezone.now().year
            if year_start > current_year:
                raise ValidationError('Tahun mulai tidak boleh lebih dari tahun sekarang.')
            if year_start < 1000:
                raise ValidationError('Tahun mulai tidak valid.')
        return year_start
    
    def clean_year_end(self):
        year_end = self.cleaned_data.get('year_end')
        year_start = self.cleaned_data.get('year_start')
        
        if year_end:
            current_year = timezone.now().year
            if year_end > current_year:
                raise ValidationError('Tahun berakhir tidak boleh lebih dari tahun sekarang.')
            if year_start and year_end < year_start:
                raise ValidationError('Tahun berakhir tidak boleh lebih kecil dari tahun mulai.')
        return year_end
    
    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        
        if period_start and period_end:
            if period_end < period_start:
                raise ValidationError('Periode berakhir tidak boleh lebih awal dari periode mulai.')
        
        return cleaned_data


class VillageHistoryPhotoForm(forms.ModelForm):
    """Form untuk Foto Sejarah Desa"""
    
    class Meta:
        model = VillageHistoryPhoto
        fields = [
            'history', 'image', 'caption', 'description', 'photographer',
            'photo_date', 'location', 'is_featured', 'is_active', 'display_order'
        ]
        widgets = {
            'history': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Keterangan singkat foto...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Deskripsi detail foto...'
            }),
            'photographer': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nama fotografer...'
            }),
            'photo_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Lokasi pengambilan foto...'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '1'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
        labels = {
            'history': 'Sejarah Terkait',
            'image': 'File Foto',
            'caption': 'Keterangan Foto',
            'description': 'Deskripsi',
            'photographer': 'Fotografer',
            'photo_date': 'Tanggal Foto',
            'location': 'Lokasi',
            'display_order': 'Urutan Tampil',
            'is_featured': 'Foto Utama',
            'is_active': 'Status Aktif'
        }
        help_texts = {
            'caption': 'Keterangan singkat yang akan ditampilkan di bawah foto',
            'description': 'Deskripsi detail tentang foto ini',
            'photographer': 'Nama orang yang mengambil foto',
            'photo_date': 'Tanggal pengambilan foto',
            'location': 'Lokasi dimana foto diambil',
            'display_order': 'Urutan tampil foto (angka kecil tampil lebih dulu)',
            'is_featured': 'Centang jika ini foto utama untuk sejarah ini',
            'is_active': 'Centang untuk mengaktifkan foto ini'
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validasi ukuran file (maksimal 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Ukuran file foto maksimal 5MB.')
            
            # Validasi format file
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if image.content_type not in allowed_formats:
                raise ValidationError('Format file harus JPEG, PNG, atau GIF.')
        
        return image
    
    def clean_display_order(self):
        display_order = self.cleaned_data.get('display_order')
        if display_order and display_order < 1:
            raise ValidationError('Urutan tampil minimal 1.')
        return display_order


class VillageHistorySearchForm(forms.Form):
    """Form untuk pencarian sejarah desa"""
    
    search_query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Cari sejarah desa...'
        }),
        label='Kata Kunci'
    )
    
    history_type = forms.ChoiceField(
        choices=[('', 'Semua Jenis')] + VillageHistory.HISTORY_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        }),
        label='Jenis Sejarah'
    )
    
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
        }),
        label='Hanya yang Ditampilkan di Beranda'
    )
    
    is_active_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
        }),
        label='Hanya yang Aktif'
    )