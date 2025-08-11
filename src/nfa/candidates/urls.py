from django.urls import path
from .views import upload_schedule, contact_us

urlpatterns = [
    path('upload-schedule/', upload_schedule, name='upload-schedule'),
    path('contact-us/', contact_us, name='contact-us'),
]
