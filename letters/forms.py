from django import forms
from django.contrib.auth import get_user_model
from .models import (
    LetterType,
    Letter,
    LetterRecipient,
    LetterAttachment,
    LetterTracking
)
from references.models import Penduduk

User = get_user_model()


class LetterTypeForm(forms.ModelForm):
    class Meta:
        model = LetterType
        fields = [
            'name', 'code', 'description', 'template_file',
            'required_documents', 'processing_time_days', 'fee_amount', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'style': 'text-transform: uppercase;'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'template_file': forms.FileInput(attrs={'class': 'form-control'}),
            'required_documents': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Pisahkan dengan koma'}),
            'processing_time_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'fee_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LetterForm(forms.ModelForm):
    class Meta:
        model = Letter
        fields = [
            'letter_type', 'applicant', 'subject', 'content', 'purpose',
            'priority', 'notes'
        ]
        widgets = {
            'letter_type': forms.Select(attrs={'class': 'form-control'}),
            'applicant': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['applicant'].queryset = Penduduk.objects.all()
        self.fields['letter_type'].queryset = LetterType.objects.filter(is_active=True)


class LetterStatusForm(forms.ModelForm):
    class Meta:
        model = Letter
        fields = ['status', 'rejection_reason', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make rejection_reason required only when status is 'rejected'
        if self.data.get('status') == 'rejected':
            self.fields['rejection_reason'].required = True
        else:
            self.fields['rejection_reason'].required = False


class LetterRecipientForm(forms.ModelForm):
    class Meta:
        model = LetterRecipient
        fields = [
            'recipient_type', 'name', 'position', 'organization',
            'address', 'phone', 'email', 'delivery_method', 'is_primary'
        ]
        widgets = {
            'recipient_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'delivery_method': forms.Select(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LetterAttachmentForm(forms.ModelForm):
    class Meta:
        model = LetterAttachment
        fields = ['attachment_type', 'title', 'description', 'file', 'is_required']
        widgets = {
            'attachment_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LetterTrackingForm(forms.ModelForm):
    class Meta:
        model = LetterTracking
        fields = ['action', 'description', 'location', 'notes']
        widgets = {
            'action': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LetterSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari berdasarkan nomor surat, perihal, atau pemohon...',
            'autocomplete': 'off'
        }),
        required=False
    )
    letter_type = forms.ModelChoiceField(
        queryset=LetterType.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label='Semua Jenis Surat'
    )
    status = forms.ChoiceField(
        choices=[('', 'Semua Status')] + Letter.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    priority = forms.ChoiceField(
        choices=[('', 'Semua Prioritas')] + Letter.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False,
        label='Dari Tanggal'
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False,
        label='Sampai Tanggal'
    )


class LetterDeliveryForm(forms.ModelForm):
    class Meta:
        model = LetterRecipient
        fields = ['delivery_date', 'received_date']
        widgets = {
            'delivery_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'received_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class BulkLetterActionForm(forms.Form):
    ACTION_CHOICES = [
        ('', 'Pilih Aksi'),
        ('approve', 'Setujui'),
        ('reject', 'Tolak'),
        ('complete', 'Selesaikan'),
        ('cancel', 'Batalkan'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alasan (opsional)'}),
        required=False
    )
    selected_letters = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )