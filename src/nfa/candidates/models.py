import os
from django.db import models
from django.utils import timezone
import uuid
import re

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