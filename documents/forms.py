from django import forms
from .models import (
    DocumentType,
    Document,
    DocumentRequest,
    DocumentApproval,
    DocumentTemplate
)


class DocumentTypeForm(forms.ModelForm):
    class Meta:
        model = DocumentType
        fields = ['name', 'description', 'required_fields', 'processing_time_days', 'fee', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'required_fields': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'JSON format'}),
            'processing_time_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'document_type', 'applicant', 'document_number', 'title', 'content',
            'status', 'priority', 'submission_date', 'completion_date',
            'notes', 'file_attachment'
        ]
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'applicant': forms.Select(attrs={'class': 'form-control'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'submission_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'completion_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file_attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DocumentRequestForm(forms.ModelForm):
    class Meta:
        model = DocumentRequest
        fields = [
            'document_type', 'requester', 'purpose', 'additional_info',
            'expected_completion_date', 'supporting_documents', 'notes'
        ]
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'requester': forms.Select(attrs={'class': 'form-control'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'expected_completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supporting_documents': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DocumentApprovalForm(forms.ModelForm):
    class Meta:
        model = DocumentApproval
        fields = [
            'document', 'approver', 'approval_level', 'status',
            'approval_date', 'comments', 'signature', 'is_final_approval'
        ]
        widgets = {
            'document': forms.Select(attrs={'class': 'form-control'}),
            'approver': forms.Select(attrs={'class': 'form-control'}),
            'approval_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'approval_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'signature': forms.FileInput(attrs={'class': 'form-control'}),
            'is_final_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DocumentTemplateForm(forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = [
            'name', 'template_type', 'document_type', 'content_template',
            'variables', 'header_template', 'footer_template',
            'is_default', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'template_type': forms.Select(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'content_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'variables': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'JSON format'}),
            'header_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'footer_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }