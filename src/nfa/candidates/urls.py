from django.urls import path
from .views import upload_schedule, contact_us, get_documents, upload_document, delete_document, replace_document

urlpatterns = [
    path('upload-schedule/', upload_schedule, name='upload-schedule'),
    path('contact-us/', contact_us, name='contact-us'),

    path('documents/', get_documents, name='get-documents'),
    path('documents/upload/', upload_document, name='upload-document'),
    path('documents/<int:pk>/delete/', delete_document, name='delete-document'),
    path('documents/<int:pk>/replace/', replace_document, name='replace-document'),
]
