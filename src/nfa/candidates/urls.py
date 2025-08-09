from django.urls import path
from .views import upload_schedule

urlpatterns = [
    path('upload-schedule/', upload_schedule, name='upload-schedule'),
]
