from django.contrib import admin
from .models import Candidate, JobPost, TestSchedule


class TestScheduleInline(admin.TabularInline):
    model = TestSchedule
    extra = 0
    readonly_fields = ('job_post', 'paper', 'test_date', 'session', 'reporting_time', 'conduct_time')
    can_delete = False


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('roll_no', 'name', 'cnic', 'mobile_no')
    search_fields = ('name', 'cnic') 
    inlines = [TestScheduleInline]


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('code', 'title')
    search_fields = ('code', 'title')


@admin.register(TestSchedule)
class TestScheduleAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job_post', 'test_date', 'session')
    search_fields = ('candidate__name', 'candidate__cnic', 'job_post__title')
