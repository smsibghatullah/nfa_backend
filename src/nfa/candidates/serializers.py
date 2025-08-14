from rest_framework import serializers
from .models import ContactRequest, Document


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
