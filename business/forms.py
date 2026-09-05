from django import forms
from .models import (BusinessCategory, Business, BusinessOwner, BusinessProduct, BusinessFinance,
                    Koperasi, BUMG, UKM, Aset, LayananJasa, JenisKoperasi)


class BusinessCategoryForm(forms.ModelForm):
    class Meta:
        model = BusinessCategory
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = '__all__'
        widgets = {
            'established_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class BusinessOwnerForm(forms.ModelForm):
    class Meta:
        model = BusinessOwner
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class BusinessProductForm(forms.ModelForm):
    class Meta:
        model = BusinessProduct
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class BusinessFinanceForm(forms.ModelForm):
    class Meta:
        model = BusinessFinance
        fields = '__all__'
        widgets = {
            'transaction_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class JenisKoperasiForm(forms.ModelForm):
    class Meta:
        model = JenisKoperasi
        fields = '__all__'
        widgets = {
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
        }


class KoperasiForm(forms.ModelForm):
    class Meta:
        model = Koperasi
        fields = '__all__'
        widgets = {
            'tanggal_berdiri': forms.DateInput(attrs={'type': 'date'}),
            'alamat': forms.Textarea(attrs={'rows': 3}),
            'jenis_usaha': forms.Textarea(attrs={'rows': 3}),
            'keterangan': forms.Textarea(attrs={'rows': 3}),
        }


class BUMGForm(forms.ModelForm):
    class Meta:
        model = BUMG
        fields = '__all__'
        widgets = {
            'tanggal_sk': forms.DateInput(attrs={'type': 'date'}),
            'alamat': forms.Textarea(attrs={'rows': 3}),
            'bidang_usaha': forms.Textarea(attrs={'rows': 3}),
            'keterangan': forms.Textarea(attrs={'rows': 3}),
        }


class UKMForm(forms.ModelForm):
    class Meta:
        model = UKM
        fields = '__all__'
        widgets = {
            'tanggal_berdiri': forms.DateInput(attrs={'type': 'date'}),
            'alamat': forms.Textarea(attrs={'rows': 3}),
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
        }


class AsetForm(forms.ModelForm):
    class Meta:
        model = Aset
        fields = '__all__'
        widgets = {
            'tanggal_perolehan': forms.DateInput(attrs={'type': 'date'}),
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
        }


class LayananJasaForm(forms.ModelForm):
    class Meta:
        model = LayananJasa
        fields = '__all__'
        widgets = {
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
        }