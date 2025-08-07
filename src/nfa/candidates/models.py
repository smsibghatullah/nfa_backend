from django.db import models

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
    
    def __str__(self):
        return f"TestSchedule for {self.candidate.roll_no} - {self.job_post.code} on {self.test_date}"

