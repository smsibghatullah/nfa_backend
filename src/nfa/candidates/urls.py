from django.urls import path
from .views import upload_schedule, contact_us, get_documents, upload_document, get_my_profile, create_profile, update_profile, list_job_listings, retrieve_job_listing, application_eligibility_check, create_job_application, review_job_application, confirm_job_application, upload_application_file

urlpatterns = [
    path('upload-schedule/', upload_schedule, name='upload-schedule'),
    path('contact-us/', contact_us, name='contact-us'),

    path('documents/', get_documents, name='get-documents'),
    path('documents/upload/', upload_document, name='upload-document'),

    path('profile/me/', get_my_profile, name='get-my-profile'),
    path('profile/', create_profile, name='create-profile'),
    path('profile/<int:pk>/', update_profile, name='update-profile'),

    path('joblistings/', list_job_listings, name='list-job-listings'),
    path('joblistings/<int:pk>/', retrieve_job_listing, name='retrieve-job-listing'),

    path('applications/eligibility-check/', application_eligibility_check, name='application-eligibility-check'),
    path('applications/upload-file/', upload_application_file, name='upload-application-file'),
    path('applications/create-job-application', create_job_application, name='create-job-application'),
    path('applications/<int:application_id>/review/', review_job_application, name='review-job-application'),
    path('applications/<int:application_id>/confirm/', confirm_job_application, name='confirm-job-application'),
]
