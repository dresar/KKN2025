from django import forms
from .models import Dusun, Lorong, Penduduk, DisabilitasType, DisabilitasData, ReligionReference, Family


class DusunForm(forms.ModelForm):
    class Meta:
        model = Dusun
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'area_size': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'name': 'Nama Dusun',
            'code': 'Kode Dusun',
            'area_size': 'Luas Area (Hektar)',
            'population_count': 'Jumlah Penduduk',
            'description': 'Deskripsi',
            'is_active': 'Aktif',
        }


class LorongForm(forms.ModelForm):
    class Meta:
        model = Lorong
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'length': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'name': 'Nama Lorong',
            'code': 'Kode Lorong',
            'dusun': 'Dusun',
            'length': 'Panjang (Meter)',
            'house_count': 'Jumlah Rumah',
            'description': 'Deskripsi',
            'is_active': 'Aktif',
        }


class PendudukForm(forms.ModelForm):
    class Meta:
        model = Penduduk
        fields = '__all__'
        exclude = ['created_by', 'updated_by']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'death_date': forms.DateInput(attrs={'type': 'date'}),
            'passport_expiry': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'height': forms.NumberInput(attrs={'min': '0', 'max': '300'}),
            'weight': forms.NumberInput(attrs={'min': '0', 'max': '500'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '08123456789'}),
            'mobile_number': forms.TextInput(attrs={'placeholder': '08123456789'}),
            'rt_number': forms.TextInput(attrs={'maxlength': '3'}),
            'rw_number': forms.TextInput(attrs={'maxlength': '3'}),
            'postal_code': forms.TextInput(attrs={'maxlength': '5'}),
        }
    
    def clean_nik(self):
        nik = self.cleaned_data.get('nik')
        if nik:
            # Check for duplicate NIK
            queryset = Penduduk.objects.filter(nik=nik)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError('NIK sudah terdaftar dalam sistem.')
        return nik
    
    def clean_kk_number(self):
        kk_number = self.cleaned_data.get('kk_number')
        # Just validate the kk_number format here, don't create Family yet
        # Family creation will be handled in save() method when all data is available
        return kk_number
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Auto-grouping: if KK number is provided, handle family creation/linking
        if instance.kk_number:
            try:
                # Find existing family with same KK number
                family = Family.objects.get(kk_number=instance.kk_number)
                if family.head and not instance.family_head:
                    # If family has a head and this person doesn't have family_head set
                    instance.family_head = family.head
                elif not family.head and not instance.family_head:
                    # If family doesn't have a head, make this person the head
                    family.head = instance
                    if commit:
                        family.save()
            except Family.DoesNotExist:
                # Create new family if it doesn't exist
                if commit:
                    instance.save()  # Save instance first to get ID
                    family = Family.objects.create(
                        kk_number=instance.kk_number,
                        head=instance,
                        dusun=instance.dusun,
                        lorong=instance.lorong,
                        address=instance.address,
                        rt_number=instance.rt_number,
                        rw_number=instance.rw_number,
                        house_number=instance.house_number,
                        postal_code=instance.postal_code,
                    )
                    return instance
        
        if commit:
            instance.save()
        return instance

        labels = {
            'nik': 'NIK',
            'name': 'Nama Lengkap',
            'gender': 'Jenis Kelamin',
            'birth_place': 'Tempat Lahir',
            'birth_date': 'Tanggal Lahir',
            'religion': 'Agama',
            'education': 'Pendidikan',
            'occupation': 'Pekerjaan',
            'marital_status': 'Status Perkawinan',
            'kk_number': 'Nomor Kartu Keluarga',
            'family_head': 'Kepala Keluarga',
            'relationship_to_head': 'Hubungan dengan Kepala Keluarga',
            'blood_type': 'Golongan Darah',
            'height': 'Tinggi Badan (cm)',
            'weight': 'Berat Badan (kg)',
            'phone_number': 'Nomor Telepon',
            'mobile_number': 'Nomor HP',
            'email': 'Email',
            'dusun': 'Dusun',
            'lorong': 'Lorong',
            'rt_number': 'Nomor RT',
            'rw_number': 'Nomor RW',
            'house_number': 'Nomor Rumah',
            'address': 'Alamat Lengkap',
            'postal_code': 'Kode Pos',
            'citizenship': 'Kewarganegaraan',
            'passport_number': 'Nomor Paspor',
            'passport_expiry': 'Berlaku Hingga',
            'emergency_contact': 'Kontak Darurat',
            'emergency_phone': 'Telepon Darurat',
            'emergency_relationship': 'Hubungan dengan Kontak Darurat',
            'is_active': 'Aktif',
            'is_alive': 'Masih Hidup',
            'death_date': 'Tanggal Meninggal',
            'death_place': 'Tempat Meninggal',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make family_head choices more user-friendly
        if 'family_head' in self.fields:
            self.fields['family_head'].queryset = Penduduk.objects.filter(is_active=True).order_by('name')
            self.fields['family_head'].empty_label = "Pilih Kepala Keluarga (kosongkan jika kepala keluarga)"
        
        # Make dusun and lorong choices more user-friendly
        if 'dusun' in self.fields:
            self.fields['dusun'].queryset = Dusun.objects.filter(is_active=True).order_by('name')
        
        if 'lorong' in self.fields:
            self.fields['lorong'].queryset = Lorong.objects.filter(is_active=True).order_by('name')
            self.fields['lorong'].empty_label = "Pilih Lorong (opsional)"


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'total_income': forms.NumberInput(attrs={'step': '1000', 'min': '0'}),
            'rt_number': forms.TextInput(attrs={'maxlength': '3'}),
            'rw_number': forms.TextInput(attrs={'maxlength': '3'}),
            'postal_code': forms.TextInput(attrs={'maxlength': '5'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '08123456789'}),
        }
        labels = {
            'kk_number': 'Nomor Kartu Keluarga',
            'head': 'Kepala Keluarga',
            'family_status': 'Status Keluarga',
            'total_members': 'Jumlah Anggota',
            'total_income': 'Total Pendapatan per Bulan (Rp)',
            'address': 'Alamat Keluarga',
            'dusun': 'Dusun',
            'lorong': 'Lorong',
            'rt_number': 'Nomor RT',
            'rw_number': 'Nomor RW',
            'house_number': 'Nomor Rumah',
            'postal_code': 'Kode Pos',
            'phone_number': 'Nomor Telepon',
            'is_active': 'Aktif',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make head choices more user-friendly
        if 'head' in self.fields:
            self.fields['head'].queryset = Penduduk.objects.filter(is_active=True).order_by('name')
        
        # Make dusun and lorong choices more user-friendly
        if 'dusun' in self.fields:
            self.fields['dusun'].queryset = Dusun.objects.filter(is_active=True).order_by('name')
        
        if 'lorong' in self.fields:
            self.fields['lorong'].queryset = Lorong.objects.filter(is_active=True).order_by('name')
            self.fields['lorong'].empty_label = "Pilih Lorong (opsional)"


class DisabilitasTypeForm(forms.ModelForm):
    class Meta:
        model = DisabilitasType
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'Nama Jenis Disabilitas',
            'code': 'Kode',
            'description': 'Deskripsi',
            'is_active': 'Aktif',
        }


class DisabilitasDataForm(forms.ModelForm):
    class Meta:
        model = DisabilitasData
        fields = '__all__'
        widgets = {
            'diagnosis_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'penduduk': 'Penduduk',
            'disability_type': 'Jenis Disabilitas',
            'severity': 'Tingkat Keparahan',
            'description': 'Deskripsi',
            'diagnosis_date': 'Tanggal Diagnosis',
            'needs_assistance': 'Memerlukan Bantuan',
            'is_active': 'Aktif',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make choices more user-friendly
        if 'penduduk' in self.fields:
            self.fields['penduduk'].queryset = Penduduk.objects.filter(is_active=True).order_by('name')
        
        if 'disability_type' in self.fields:
            self.fields['disability_type'].queryset = DisabilitasType.objects.filter(is_active=True).order_by('name')


class ReligionReferenceForm(forms.ModelForm):
    class Meta:
        model = ReligionReference
        fields = '__all__'
        labels = {
            'name': 'Nama Agama',
            'code': 'Kode',
            'is_active': 'Aktif',
        }