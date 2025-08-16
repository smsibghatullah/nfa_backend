import os
import uuid
import re
from django.db import models, transaction
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field
from .utils import html_to_pdf_bytes


def contact_upload_path(instance, filename):
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', instance.name.replace(' ', '_')).lower()
    base, ext = os.path.splitext(filename)
    unique_name = f"{safe_name}_{base}_{uuid.uuid4().hex}{ext}"
    now = timezone.now()
    return os.path.join('contact_uploads', now.strftime('%Y/%m/%d'), unique_name)


class JobPost(models.Model):
    code = models.CharField(max_length=20, unique=True, help_text="Short code or abbreviation e.g. 'NQ (1)'")
    title = models.CharField(max_length=200, help_text="Full job post name, e.g. 'Naib Qasid Male (NFAPS-1)'")
    description = models.TextField(blank=True, null=True, help_text="Optional detailed description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} [{self.code}]"


class Candidate(models.Model):
    roll_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    cnic = models.CharField(max_length=20, unique=True)
    postal_address = models.TextField()
    mobile_no = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.roll_no} - {self.name}"


class TestSchedule(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='test_schedules')
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='test_schedules')
    paper = models.CharField(max_length=50)
    test_date = models.DateField()
    session = models.CharField(max_length=50)
    reporting_time = models.CharField(max_length=20)
    conduct_time = models.CharField(max_length=50)
    venue = models.TextField(blank=True, null=True, help_text="Test venue/location")

    def __str__(self):
        return f"TestSchedule for {self.candidate.roll_no} - {self.job_post.code} on {self.test_date} at {self.venue or 'N/A'}"


class ContactRequest(models.Model):
    SERVICE_CHOICES = [
        ('fingerprint_analysis', 'Fingerprint Analysis'),
        ('digital_forensics', 'Digital Forensics'),
        ('narcotics_analysis', 'Narcotics Analysis'),
        ('crime_scene_investigation', 'Crime Scene Investigation'),
        ('firearms_tool_marks', 'Firearms & Tool Marks'),
        ('dna_forensics', 'DNA Forensics'),
        ('questioned_documents', 'Questioned Documents'),
        ('toxicology', 'Toxicology'),
        ('serology', 'Serology'),
        ('pathology', 'Pathology'),
        ('explosives_analysis', 'Explosives Analysis'),
    ]

    PREFERRED_CONTACT_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    service = models.CharField(max_length=100, choices=SERVICE_CHOICES)
    description = models.TextField(blank=True, null=True)
    preferred_contact = models.CharField(max_length=10, choices=PREFERRED_CONTACT_CHOICES)
    file = models.FileField(upload_to=contact_upload_path, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.service} ({self.submitted_at.strftime('%Y-%m-%d %H:%M')})"


class Document(models.Model):
    name = models.CharField(max_length=255, help_text="Display name of the document")
    purpose = models.TextField(blank=True, help_text="Purpose or description of the document")
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name


class Advertisement(models.Model):
    title = models.CharField(max_length=255)
    html_content = CKEditor5Field('HTML Content', config_name='default')
    document = models.OneToOneField(
        Document, on_delete=models.CASCADE, null=True, blank=True, related_name='advertisement'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def _build_pdf_filename(self) -> str:
        base = re.sub(r'[^a-zA-Z0-9_-]+', '_', self.title.strip())[:60] or "advertisement"
        return f"advertisement_{base}_{uuid.uuid4().hex}.pdf"

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        pdf_bytes = html_to_pdf_bytes(self.html_content or "")
        filename = self._build_pdf_filename()

        if self.document_id:
            doc = self.document
            if doc.file:
                try:
                    doc.file.delete(save=False)
                except Exception:
                    pass
            doc.name = self.title
            doc.purpose = "Advertisement"
            doc.file.save(filename, ContentFile(pdf_bytes), save=True)
        else:
            doc = Document.objects.create(name=self.title, purpose="Advertisement")
            doc.file.save(filename, ContentFile(pdf_bytes), save=True)
            self.document = doc
            super().save(update_fields=["document"])

        Document.objects.filter(pk=self.document.pk).update(
            uploaded_at=self.created_at,
            last_updated=self.updated_at,
        )

@receiver(post_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    if instance.file:
        try:
            instance.file.delete(save=False)
        except Exception:
            pass


@receiver(post_delete, sender=Advertisement)
def delete_advertisement_document(sender, instance, **kwargs):
    if instance.document:
        instance.document.delete()
