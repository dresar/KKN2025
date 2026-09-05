from django.db import models
from django.contrib.auth import get_user_model
from references.models import Penduduk

User = get_user_model()


class DocumentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    required_fields = models.JSONField(default=dict, blank=True)
    processing_time_days = models.PositiveIntegerField(default=3)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Jenis Dokumen'
        verbose_name_plural = 'Jenis Dokumen'


class Document(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Diajukan'),
        ('processing', 'Diproses'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('completed', 'Selesai'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Rendah'),
        ('normal', 'Normal'),
        ('high', 'Tinggi'),
        ('urgent', 'Mendesak'),
    ]
    
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    applicant = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='documents')
    document_number = models.CharField(max_length=50, unique=True, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    submission_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    file_attachment = models.FileField(upload_to='documents/', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.document_number} - {self.title}'

    class Meta:
        verbose_name = 'Dokumen'
        verbose_name_plural = 'Dokumen'
        ordering = ['-created_at']


class DocumentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('cancelled', 'Dibatalkan'),
    ]
    
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    requester = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='document_requests')
    purpose = models.CharField(max_length=200)
    additional_info = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    supporting_documents = models.FileField(upload_to='document_requests/', blank=True)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.requester.nama} - {self.document_type.name}'

    class Meta:
        verbose_name = 'Permintaan Dokumen'
        verbose_name_plural = 'Permintaan Dokumen'
        ordering = ['-request_date']


class DocumentApproval(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu Persetujuan'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('revision_required', 'Perlu Revisi'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    approval_level = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approval_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    signature = models.ImageField(upload_to='signatures/', blank=True)
    is_final_approval = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.document.title} - {self.approver.username}'

    class Meta:
        verbose_name = 'Persetujuan Dokumen'
        verbose_name_plural = 'Persetujuan Dokumen'
        unique_together = ['document', 'approver', 'approval_level']
        ordering = ['approval_level', '-created_at']


class DocumentTemplate(models.Model):
    TEMPLATE_TYPE_CHOICES = [
        ('surat_keterangan', 'Surat Keterangan'),
        ('surat_pengantar', 'Surat Pengantar'),
        ('surat_izin', 'Surat Izin'),
        ('surat_rekomendasi', 'Surat Rekomendasi'),
        ('formulir', 'Formulir'),
        ('lainnya', 'Lainnya'),
    ]
    
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPE_CHOICES)
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, related_name='templates')
    content_template = models.TextField()
    variables = models.JSONField(default=dict, blank=True)
    header_template = models.TextField(blank=True)
    footer_template = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Template Dokumen'
        verbose_name_plural = 'Template Dokumen'
        ordering = ['name']
