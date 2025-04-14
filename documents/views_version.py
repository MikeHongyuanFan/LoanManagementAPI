from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Document
from .serializers import DocumentSerializer
from django.shortcuts import get_object_or_404
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_document_version(request, document_id):
    """Create a new version of a document"""
    try:
        parent_document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if file is provided
    if 'file' not in request.FILES:
        return Response({"file": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get the latest version number
    latest_version = Document.objects.filter(parent_document=parent_document).order_by('-version').first()
    new_version_number = (latest_version.version + 1) if latest_version else 2
    
    # Create new document version
    new_document = Document.objects.create(
        title=parent_document.title,
        description=parent_document.description,
        document_type=parent_document.document_type,
        category=parent_document.category,
        file=request.FILES['file'],
        parent_document=parent_document,
        version=new_version_number,
        version_notes=request.data.get('version_notes', ''),
        is_latest_version=True,
        uploaded_by=request.user,
        last_modified_by=request.user,
        status='draft'
    )
    
    # Update tags and collections
    if parent_document.tags.exists():
        new_document.tags.set(*[parent_document.tags.names()])
    
    if parent_document.collections.exists():
        new_document.collections.set(parent_document.collections.all())
    
    # Update previous version to not be the latest
    parent_document.is_latest_version = False
    parent_document.save()
    
    # Serialize and return the new document
    serializer = DocumentSerializer(new_document)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_document_versions(request, document_id):
    """Get all versions of a document"""
    try:
        document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Find the root document (version 1)
    root_document = document
    while root_document.parent_document:
        root_document = root_document.parent_document
    
    # Get all versions
    versions = [root_document]
    versions.extend(Document.objects.filter(parent_document=root_document).order_by('version'))
    
    # Serialize and return
    serializer = DocumentSerializer(versions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revert_to_version(request, document_id, version_id):
    """Revert a document to a previous version"""
    try:
        current_document = Document.objects.get(pk=document_id)
        version_document = Document.objects.get(pk=version_id)
    except Document.DoesNotExist:
        return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Verify that version_document is a version of current_document
    root_document = current_document
    while root_document.parent_document:
        root_document = root_document.parent_document
    
    if version_document.parent_document != root_document and version_document != root_document:
        return Response(
            {"detail": "The specified version is not related to this document"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create a new version based on the old version
    new_version_number = current_document.version + 1
    
    # Copy the file from the version document
    file_path = version_document.file.path
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # Create a new file path
    new_file_path = f"documents/{request.user.id}/{timezone.now().strftime('%Y%m%d%H%M%S')}_{file_name}"
    path = default_storage.save(new_file_path, ContentFile(file_content))
    
    # Create new document version
    new_document = Document.objects.create(
        title=current_document.title,
        description=current_document.description,
        document_type=current_document.document_type,
        category=current_document.category,
        file=path,
        parent_document=root_document,
        version=new_version_number,
        version_notes=f"Reverted to version {version_document.version}",
        is_latest_version=True,
        uploaded_by=request.user,
        last_modified_by=request.user,
        status='draft'
    )
    
    # Update tags and collections
    if current_document.tags.exists():
        new_document.tags.set(*[current_document.tags.names()])
    
    if current_document.collections.exists():
        new_document.collections.set(current_document.collections.all())
    
    # Update previous version to not be the latest
    current_document.is_latest_version = False
    current_document.save()
    
    # Serialize and return the new document
    serializer = DocumentSerializer(new_document)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def compare_versions(request, version1_id, version2_id):
    """Compare two versions of a document"""
    try:
        version1 = Document.objects.get(pk=version1_id)
        version2 = Document.objects.get(pk=version2_id)
    except Document.DoesNotExist:
        return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Verify that both documents are related
    root1 = version1
    while root1.parent_document:
        root1 = root1.parent_document
    
    root2 = version2
    while root2.parent_document:
        root2 = root2.parent_document
    
    if root1.id != root2.id:
        return Response(
            {"detail": "The specified versions are not related"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # For now, just return basic metadata comparison
    # In a real implementation, you would use a document comparison library
    comparison = {
        "version1": {
            "id": version1.id,
            "version": version1.version,
            "title": version1.title,
            "uploaded_by": version1.uploaded_by.username,
            "created_at": version1.created_at,
            "file_size": version1.file.size if version1.file else 0
        },
        "version2": {
            "id": version2.id,
            "version": version2.version,
            "title": version2.title,
            "uploaded_by": version2.uploaded_by.username,
            "created_at": version2.created_at,
            "file_size": version2.file.size if version2.file else 0
        },
        "differences": {
            "title": version1.title != version2.title,
            "description": version1.description != version2.description,
            "document_type": version1.document_type != version2.document_type,
            "category": version1.category != version2.category if version1.category and version2.category else None,
            "file": version1.file != version2.file
        }
    }
    
    return Response(comparison)
