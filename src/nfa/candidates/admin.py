from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from .models import (Candidate, JobPost, TestSchedule, 
                     ContactRequest, Document, Advertisement,
                     Profile, Education, WorkHistory, JobListing,
                     JobQuestion, JobApplication, ApplicationDocument, ApplicationAnswer)
from .views import upload_schedule

class TestScheduleInline(admin.TabularInline):
    model = TestSchedule
    extra = 0
    readonly_fields = ('job_post', 'paper', 'test_date', 'session', 'reporting_time', 'conduct_time')
    can_delete = False

@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = [field.name for field in Profile._meta.get_fields() if not field.many_to_many and not field.one_to_many]

@admin.register(Education)
class EducationAdmin(ModelAdmin):
    list_display = [field.name for field in Education._meta.get_fields() if not field.many_to_many and not field.one_to_many]

@admin.register(WorkHistory)
class WorkHistoryAdmin(ModelAdmin):
    list_display = [field.name for field in WorkHistory._meta.get_fields() if not field.many_to_many and not field.one_to_many]

@admin.register(JobListing)
class JobListing(ModelAdmin):
    list_display = [field.name for field in JobListing._meta.get_fields() if not field.many_to_many and not field.one_to_many]

@admin.register(JobQuestion)
class JobQuestion(ModelAdmin):
    list_display = [field.name for field in JobQuestion._meta.get_fields() if not field.many_to_many and not field.one_to_many]

@admin.register(JobApplication)
class JobApplication(ModelAdmin):
    list_display = [field.name for field in JobApplication._meta.get_fields() if not field.many_to_many and not field.one_to_many]

@admin.register(ApplicationDocument)
class ApplicationDocument(ModelAdmin):
    list_display = [field.name for field in ApplicationDocument._meta.get_fields() if not field.many_to_many and not field.one_to_many]

@admin.register(ApplicationAnswer)
class ApplicationAnswer(ModelAdmin):
    list_display = [field.name for field in ApplicationAnswer._meta.get_fields() if not field.many_to_many and not field.one_to_many]

@admin.register(Candidate)
class CandidateAdmin(ModelAdmin):
    list_display = ('roll_no', 'name', 'cnic', 'mobile_no')
    search_fields = ('name', 'cnic')
    inlines = [TestScheduleInline]
    change_list_template = "admin/candidates/candidates_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom-search/', self.admin_site.admin_view(self.custom_search), name="candidate-search"),
            path('upload-schedule/', self.admin_site.admin_view(upload_schedule), name="candidate-upload-schedule"),
            path('submitted-forms/', self.admin_site.admin_view(self.submitted_forms), name="submitted-forms"),
        ]
        return custom_urls + urls

    def custom_search(self, request):
        context = dict(self.admin_site.each_context(request))
        query = request.GET.get('q', '').strip()
        candidates = []
        if query:
            candidates = (Candidate.objects.filter(name__icontains=query) |
                          Candidate.objects.filter(cnic__icontains=query))
        context['candidates'] = candidates
        context['query'] = query
        return render(request, 'admin/candidates/search.html', context)

    def submitted_forms(self, request):
        context = dict(self.admin_site.each_context(request))
        context['forms'] = ContactRequest.objects.all().order_by('-submitted_at')
        return render(request, 'admin/candidates/submitted_forms.html', context)

@admin.register(JobPost)
class JobPostAdmin(ModelAdmin):
    list_display = ('code', 'title')
    search_fields = ('code', 'title')

@admin.register(TestSchedule)
class TestScheduleAdmin(ModelAdmin):
    list_display = ('candidate', 'job_post', 'test_date', 'session')
    search_fields = ('candidate__name', 'candidate__cnic', 'job_post__title')

@admin.register(ContactRequest)
class ContactRequestAdmin(ModelAdmin):
    list_display = ('name', 'email', 'phone', 'service', 'preferred_contact', 'submitted_at', 'file_link')
    list_filter = ('service', 'preferred_contact', 'submitted_at')
    search_fields = ('name', 'email', 'phone')
    ordering = ('-submitted_at',)

    def file_link(self, obj):
        if obj.file:
            return format_html("<a href='{}' download>Download</a>", obj.file.url)
        return "-"
    file_link.short_description = "File"

@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ('name', 'purpose', 'uploaded_at', 'download_link')
    search_fields = ('name', 'purpose')
    ordering = ('-uploaded_at',)

    def download_link(self, obj):
        if obj.file:
            return format_html("<a href='{}' target='_blank'>View</a>", obj.file.url)
        return "-"
    download_link.short_description = "Document"

@admin.register(Advertisement)
class AdvertisementAdmin(ModelAdmin):
    exclude = ("document",)
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)

original_get_app_list = admin.site.get_app_list

def get_app_list_with_ordering(request, app_label=None):
    app_list = original_get_app_list(request, app_label)
    ordering = {
        "Candidate": 4,
        "JobPost": 5,
        "TestSchedule": 6,
        "ContactRequest": 3,
        "Document": 2,
        "Advertisement": 1,
    }
    for app in app_list:
        if app['app_label'] == 'candidates':
            for model in app['models']:
                model_name = model['object_name']
                model['order'] = ordering.get(model_name, 999)
            app['models'].sort(key=lambda x: x['order'])
    return app_list

admin.site.get_app_list = get_app_list_with_ordering
