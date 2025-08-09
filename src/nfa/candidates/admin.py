from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Candidate, JobPost, TestSchedule
from .views import upload_schedule

class TestScheduleInline(admin.TabularInline):
    model = TestSchedule
    extra = 0
    readonly_fields = (
        'job_post',
        'paper',
        'test_date',
        'session',
        'reporting_time',
        'conduct_time',
    )
    can_delete = False

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('roll_no', 'name', 'cnic', 'mobile_no')
    search_fields = ('name', 'cnic')
    inlines = [TestScheduleInline]
    change_list_template = "admin/candidates/candidate_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom-search/', self.admin_site.admin_view(self.custom_search), name="candidate-search"),
            path('upload-schedule/', self.admin_site.admin_view(upload_schedule), name="candidate-upload-schedule"),
        ]
        return custom_urls + urls

    def custom_search(self, request):
        context = dict(
            self.admin_site.each_context(request),
        )

        query = request.GET.get('q', '').strip()
        candidates = []
        if query:
            candidates = Candidate.objects.filter(name__icontains=query) | Candidate.objects.filter(cnic__icontains=query)

        context['candidates'] = candidates
        context['query'] = query
        return render(request, 'admin/candidates/search.html', context)

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('code', 'title')
    search_fields = ('code', 'title')

@admin.register(TestSchedule)
class TestScheduleAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job_post', 'test_date', 'session')
    search_fields = ('candidate__name', 'candidate__cnic', 'job_post__title')