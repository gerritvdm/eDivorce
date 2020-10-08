from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Document, UserResponse
from .validators import file_scan_validation, valid_file_extension, valid_doc_type, valid_rotation


class UserResponseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    question = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserResponse
        fields = ('user', 'question', 'value')

    def create(self, validated_data):
        response = UserResponse(**validated_data)
        response.save()
        return response

    def update(self, instance, validated_data):
        instance.value = validated_data['value']
        instance.save()


class CreateDocumentSerializer(serializers.ModelSerializer):
    doc_type = serializers.CharField(required=True, validators=[valid_doc_type])
    party_code = serializers.IntegerField(min_value=0, max_value=2, required=True)
    file = serializers.FileField(required=True, validators=[valid_file_extension,file_scan_validation])
    filename = serializers.CharField(read_only=True)
    size = serializers.IntegerField(read_only=True)
    rotation = serializers.IntegerField(read_only=True)
    sort_order = serializers.IntegerField(read_only=True)
    file_url = serializers.URLField(source='get_file_url', read_only=True)

    class Meta:
        model = Document
        fields = ('file', 'doc_type', 'party_code', 'filename', 'size', 'rotation', 'sort_order', 'file_url')

    def create(self, validated_data):
        filename = validated_data['file'].name
        size = validated_data['file'].size
        user = self.context['request'].user
        order = Document.objects.filter(bceid_user=user, doc_type=validated_data['doc_type'], party_code=validated_data['party_code']).count() + 1
        response = Document(bceid_user=user, filename=filename, size=size, sort_order=order, **validated_data)
        try:
            response.save()
        except IntegrityError:
            raise ValidationError("This file appears to have already been uploaded for this document. Duplicate filename: " + filename)
        return response


class DocumentMetadataSerializer(serializers.ModelSerializer):
    doc_type = serializers.CharField(read_only=True)
    party_code = serializers.IntegerField(read_only=True)
    filename = serializers.CharField(read_only=True)
    size = serializers.IntegerField(read_only=True)
    rotation = serializers.IntegerField(min_value=0, max_value=270, validators=[valid_rotation])
    sort_order = serializers.IntegerField(read_only=True)
    file_url = serializers.URLField(source='get_file_url', read_only=True)

    class Meta:
        model = Document
        fields = ('doc_type', 'party_code', 'filename', 'size', 'rotation', 'sort_order', 'file_url')
