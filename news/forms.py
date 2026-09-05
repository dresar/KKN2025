from django import forms
from django.forms import inlineformset_factory
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from .models import (
    NewsCategory,
    NewsTag,
    News,
    NewsComment,
    NewsView,
    NewsImage,
    NewsLike,
    NewsShare,
    Announcement
)


class NewsCategoryForm(forms.ModelForm):
    class Meta:
        model = NewsCategory
        fields = ['name', 'description', 'color', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama kategori...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Deskripsi kategori (opsional)...'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control', 
                'type': 'color'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class NewsTagForm(forms.ModelForm):
    class Meta:
        model = NewsTag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama tag...'
            }),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = [
            'title', 'category', 'tags', 'content', 'excerpt', 'featured_image', 'featured_image_alt',
            'status', 'priority', 'is_featured', 'is_breaking', 'published_date', 'scheduled_date',
            'meta_title', 'meta_description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan judul berita...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'multiple': True
            }),
            'content': SummernoteWidget(attrs={
                'summernote': {
                    'width': '100%',
                    'height': '400',
                    'toolbar': [
                        ['style', ['style']],
                        ['font', ['bold', 'underline', 'clear']],
                        ['fontname', ['fontname']],
                        ['color', ['color']],
                        ['para', ['ul', 'ol', 'paragraph']],
                        ['table', ['table']],
                        ['insert', ['link', 'picture', 'video']],
                        ['view', ['fullscreen', 'codeview', 'help']],
                    ],
                    'placeholder': 'Tulis konten berita di sini...',
                }
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': '300',
                'placeholder': 'Ringkasan singkat berita (opsional)...'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'featured_image_alt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alt text untuk gambar utama (opsional)...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_breaking': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'published_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '60',
                'placeholder': 'Judul SEO (opsional)...'
            }),
            'meta_description': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '160',
                'placeholder': 'Deskripsi SEO (opsional)...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Pilih Kategori'
        self.fields['tags'].help_text = 'Pilih satu atau lebih tag (gunakan Ctrl+Click untuk multiple selection)'
        self.fields['scheduled_date'].help_text = 'Atur tanggal untuk publikasi otomatis (opsional)'
        
        # Make some fields required
        self.fields['title'].required = True
        self.fields['category'].required = True
        self.fields['content'].required = True


class NewsImageForm(forms.ModelForm):
    class Meta:
        model = NewsImage
        fields = ['image', 'caption', 'alt_text', 'is_featured', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Caption gambar (opsional)...'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alt text untuk SEO...'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True
        self.fields['alt_text'].required = True
        self.fields['order'].help_text = 'Urutan tampilan gambar (0 = pertama)'


# Formset untuk multiple images
NewsImageFormSet = inlineformset_factory(
    News, 
    NewsImage, 
    form=NewsImageForm,
    extra=3,  # Jumlah form kosong yang ditampilkan
    max_num=10,  # Maksimal 10 gambar per berita
    can_delete=True,
    fields=['image', 'caption', 'alt_text', 'is_featured', 'order']
)


class NewsCommentForm(forms.ModelForm):
    class Meta:
        model = NewsComment
        fields = ['author_name', 'author_email', 'content']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Anda...'
            }),
            'author_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Anda...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tulis komentar Anda...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author_name'].required = True
        self.fields['author_email'].required = True
        self.fields['content'].required = True


class NewsCommentModerationForm(forms.ModelForm):
    class Meta:
        model = NewsComment
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class BulkNewsActionForm(forms.Form):
    """Form untuk bulk actions pada news"""
    ACTION_CHOICES = [
        ('', 'Pilih Aksi'),
        ('publish', 'Publikasikan'),
        ('draft', 'Jadikan Draft'),
        ('archive', 'Arsipkan'),
        ('delete', 'Hapus'),
        ('featured', 'Jadikan Featured'),
        ('unfeatured', 'Hapus Featured'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    selected_news = forms.CharField(
        widget=forms.HiddenInput()
    )


class NewsImportForm(forms.Form):
    """Form untuk import news dari file"""
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        }),
        help_text='Upload file CSV atau Excel dengan format yang sesuai'
    )
    
    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            # Validasi ekstensi file
            valid_extensions = ['.csv', '.xlsx', '.xls']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in valid_extensions:
                raise forms.ValidationError('File harus berformat CSV atau Excel (.csv, .xlsx, .xls)')
            
            # Validasi ukuran file (maksimal 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Ukuran file tidak boleh lebih dari 5MB')
        
        return file


class NewsSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari berita...',
            'autocomplete': 'off'
        }),
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=NewsCategory.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label='Semua Kategori'
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=NewsTag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'excerpt', 'announcement_type', 'status', 'priority',
            'is_pinned', 'is_popup', 'start_date', 'end_date', 'target_audience',
            'contact_person', 'contact_phone', 'location'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan judul pengumuman...'
            }),
            'content': SummernoteWidget(attrs={
                'summernote': {
                    'width': '100%',
                    'height': '300',
                    'toolbar': [
                        ['style', ['style']],
                        ['font', ['bold', 'underline', 'clear']],
                        ['fontname', ['fontname']],
                        ['color', ['color']],
                        ['para', ['ul', 'ol', 'paragraph']],
                        ['table', ['table']],
                        ['insert', ['link']],
                        ['view', ['fullscreen', 'codeview', 'help']],
                    ],
                    'placeholder': 'Tulis isi pengumuman di sini...',
                }
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'maxlength': '300',
                'placeholder': 'Ringkasan singkat pengumuman (opsional)...'
            }),
            'announcement_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_popup': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'target_audience': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Semua Warga, Ibu-ibu PKK, Remaja...'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama narahubung...'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nomor telepon narahubung...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lokasi acara/kegiatan...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['start_date'].required = True


class AnnouncementSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari pengumuman...',
            'autocomplete': 'off'
        }),
        required=False
    )
    announcement_type = forms.ChoiceField(
        choices=[('', 'Semua Jenis')] + Announcement.TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    status = forms.ChoiceField(
        choices=[('', 'Semua Status')] + Announcement.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    priority = forms.ChoiceField(
        choices=[('', 'Semua Prioritas')] + Announcement.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )