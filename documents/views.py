from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .serializers import DocumentCreateSerializer, DocumentSerializer
from .models import Document
from .utils import get_name
import os
# Create your views here.

class DocumentView(APIView):

    def get(self, request):
        """
            Get all documents
        """
        serializer = DocumentSerializer(Document.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
            Create a new document
        """
        try:
            serializer = DocumentCreateSerializer(data={
                'file': request.FILES['file'],
                'name': request.data['name'],
                'description': request.data['description']
            })
            if serializer.is_valid():
                # update the file name
                request.FILES['file'].name = get_name(name=request.data['name'], originalname=request.FILES['file'].name)

                doc = Document.objects.create(
                    file=request.FILES['file'],
                    name=f"{request.data['name']}.{request.FILES['file'].name.split('.')[-1]}",
                    description=request.data['description'],
                )
                serializer = DocumentSerializer(doc)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        """
            Delete all documents
        """
        try:
            doc_id = request.query_params.get('id', None)
            doc = Document.objects.get(pk=doc_id)
            
            # delete the doc from media folder
            os.remove(doc.file.path )
            
            doc.delete()

            return Response({
                "message": "All documents deleted successfully"
            },status=status.HTTP_200_OK)        
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
