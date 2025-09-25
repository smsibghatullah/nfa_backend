import os
import uuid
import re
from django.conf import settings
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
    
class JobListing(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open / Active / Published'),
        ('closed', 'Closed / Filled / Inactive'),
        ('draft', 'Draft / Pending / Unpublished'),
        ('expired', 'Expired'),
        ('on_hold', 'On Hold / Paused / Temporarily Closed'),
        ('archived', 'Archived'),
    ]

    QUALIFICATION_CHOICES = [
        ('matric', 'Matric'),
        ('intermediate', 'Intermediate'),
        ('bachelors', 'Bachelors'),
        ('masters', 'Masters'),
    ]

    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='listings')
    location = models.CharField(max_length=255, blank=True, null=True)
    application_deadline = models.DateField()
    number_of_positions = models.PositiveIntegerField(default=1)
    salary_range = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 50000-70000 PKR")

    minimum_age = models.PositiveIntegerField(blank=True, null=True, help_text="Minimum age required")
    minimum_qualification = models.CharField(max_length=20, choices=QUALIFICATION_CHOICES, blank=True, null=True)
    required_experience = models.PositiveIntegerField(blank=True, null=True, help_text="Required experience in years")

    requirements = models.TextField(blank=True, null=True, help_text="Qualifications, experience, skills required")
    responsibilities = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True, help_text="Any extra info or instructions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-application_deadline']

    def __str__(self):
        return f"{self.job_post.title} - {self.location or 'N/A'} ({self.status})"

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
    PREFERRED_CONTACT_CHOICES = [('email', 'Email'), ('phone', 'Phone')]

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
        verbose_name = "Add Document"
        verbose_name_plural = "Add Documents"

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
                try: doc.file.delete(save=False)
                except Exception: pass
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
        try: instance.file.delete(save=False)
        except Exception: pass


@receiver(post_delete, sender=Advertisement)
def delete_advertisement_document(sender, instance, **kwargs):
    if instance.document:
        instance.document.delete()

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField()
    postal_address = models.TextField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} Profile"


class Education(models.Model):
    QUALIFICATION_CHOICES = [
        ('matric', 'Matric'),
        ('intermediate', 'Intermediate'),
        ('bachelors', 'Bachelors'),
        ('masters', 'Masters'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    institution_name = models.CharField(max_length=255)
    degree = models.CharField(max_length=20, choices=QUALIFICATION_CHOICES)
    field_of_study = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    grade = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-end_date']

    def __str__(self):
        return f"{self.degree} - {self.institution_name}"

class WorkHistory(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='work_histories')
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.job_title} - {self.company_name}"
    
def application_upload_path(instance, filename):
    return f"applications/{instance.applicant.user.id}/{uuid.uuid4().hex}_{filename}"

class JobQuestion(models.Model):
    job_listing = models.ForeignKey('JobListing', on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.job_listing.job_post.title} - {self.question_text[:50]}"

class JobApplication(models.Model):
    applicant = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='applications')
    job_listing = models.ForeignKey('JobListing', on_delete=models.CASCADE, related_name='applications')
    reference_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.reference_number} - {self.applicant.user.email}"

def application_upload_path(instance, filename):
    uid = uuid.uuid4().hex
    if getattr(instance, 'application', None):
        return f"applications/{instance.application.id}/{uid}_{filename}"
    return f"applications/temp/{uid}_{filename}"


class ApplicationDocument(models.Model):
    application = models.ForeignKey(
        'JobApplication',
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=application_upload_path)

    def __str__(self):
        return f"{self.name} - {self.application.reference_number if self.application else 'TEMP'}"

class ApplicationAnswer(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(JobQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField()

    def __str__(self):
        return f"{self.question.question_text[:50]} - {self.application.reference_number}"
