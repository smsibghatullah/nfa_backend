from rest_framework import serializers
from .models import (ContactRequest, Document,
                     Profile, Education, WorkHistory, 
                     JobListing, JobPost, 
                     JobApplication, ApplicationDocument, ApplicationAnswer, JobQuestion)

class ContactRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = '__all__'
        read_only_fields = ('submitted_at',)

    def validate(self, data):
        required_fields = ['name', 'email', 'phone', 'service', 'preferred_contact']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: "This field is required."})
        return data


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'name', 'purpose', 'file', 'uploaded_at', 'last_updated']
        read_only_fields = ['uploaded_at', 'last_updated']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ('profile',)


class WorkHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkHistory
        fields = '__all__'
        read_only_fields = ('profile',)


class ProfileSerializer(serializers.ModelSerializer):
    educations = EducationSerializer(many=True, required=False)
    work_histories = WorkHistorySerializer(many=True, required=False)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'date_of_birth', 'postal_address', 'phone_number', 'bio',
                  'educations', 'work_histories']
        read_only_fields = ['user']

    def create(self, validated_data):
        educations_data = validated_data.pop('educations', [])
        work_histories_data = validated_data.pop('work_histories', [])

        user = self.context['request'].user
        profile = Profile.objects.create(user=user, **validated_data)

        for edu_data in educations_data:
            Education.objects.create(profile=profile, **edu_data)

        for work_data in work_histories_data:
            WorkHistory.objects.create(profile=profile, **work_data)

        return profile

    def update(self, instance, validated_data):
        educations_data = validated_data.pop('educations', [])
        work_histories_data = validated_data.pop('work_histories', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if educations_data:
            instance.educations.all().delete()
            for edu_data in educations_data:
                Education.objects.create(profile=instance, **edu_data)

        if work_histories_data:
            instance.work_histories.all().delete()
            for work_data in work_histories_data:
                WorkHistory.objects.create(profile=instance, **work_data)

        return instance
    
class JobPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = ['id', 'code', 'title', 'description', 'created_at', 'updated_at']

class JobListingSerializer(serializers.ModelSerializer):
    job_post = JobPostSerializer(read_only=True)

    class Meta:
        model = JobListing
        fields = [
            'id', 'job_post', 'location', 'application_deadline',
            'number_of_positions', 'salary_range',
            'minimum_age', 'minimum_qualification', 'required_experience',
            'requirements', 'responsibilities', 'additional_info',
            'status', 'created_at', 'updated_at'
        ]

class ApplicationAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationAnswer
        fields = ['id', 'question', 'answer_text']

class UploadApplicationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = ['id', 'name', 'file']
        read_only_fields = ['id']

class JobApplicationSerializer(serializers.ModelSerializer):
    answers = serializers.ListField(write_only=True)
    document_ids = serializers.ListField(write_only=True) 

    class Meta:
        model = JobApplication
        fields = ['id', 'applicant', 'job_listing', 'reference_number', 'answers', 'document_ids']
        read_only_fields = ['id', 'reference_number', 'applicant']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        document_ids = validated_data.pop('document_ids', [])

        application = JobApplication.objects.create(**validated_data)

        for ans in answers_data:
            question = JobQuestion.objects.get(pk=ans['question'])
            ApplicationAnswer.objects.create(
                application=application,
                question=question,
                answer_text=ans['answer_text']
            )

        for doc_id in document_ids:
            try:
                doc = ApplicationDocument.objects.get(pk=doc_id)
                doc.application = application
                doc.save()
            except ApplicationDocument.DoesNotExist:
                continue

        return application

class JobApplicationReviewSerializer(serializers.ModelSerializer):
    applicant_profile = ProfileSerializer(source='applicant', read_only=True)
    job_listing_details = JobListingSerializer(source='job_listing', read_only=True)
    answers = serializers.SerializerMethodField()
    documents = UploadApplicationDocumentSerializer(many=True, read_only=True)


    class Meta:
        model = JobApplication
        fields = [
            'id', 'reference_number', 'submitted_at', 'is_confirmed',
            'applicant_profile', 'job_listing_details', 'answers', 'documents'
        ]

    def get_answers(self, obj):
        return ApplicationAnswer.objects.filter(application=obj).values('question_id', 'answer_text')
