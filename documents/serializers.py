from rest_framework import serializers
from .models import Document
# create a serializer for file upload

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'name', 'description', 'file', 'date_created', 'size']

class DocumentCreateSerializer(serializers.Serializer):
    file = serializers.FileField()
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=100, allow_blank=True, allow_null=True)

    class Meta:
        fields = ['file', 'name', 'description']