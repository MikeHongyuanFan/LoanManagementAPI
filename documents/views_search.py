from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Document, DocumentCategory, DocumentCollection
from .serializers import DocumentSerializer
from django.utils import timezone
from datetime import timedelta
import json

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def advanced_document_search(request):
    """Advanced document search with multiple filters"""
    # Start with all documents
    queryset = Document.objects.all()
    
    # Apply filters based on query parameters
    
    # Text search (title, description, keywords)
    search_text = request.query_params.get('search', None)
    if search_text:
        queryset = queryset.filter(
            Q(title__icontains=search_text) | 
            Q(description__icontains=search_text) | 
            Q(keywords__icontains=search_text)
        )
    
    # Document type
    doc_type = request.query_params.get('type', None)
    if doc_type:
        queryset = queryset.filter(document_type=doc_type)
    
    # Status
    status_param = request.query_params.get('status', None)
    if status_param:
        queryset = queryset.filter(status=status_param)
    
    # Category
    category_id = request.query_params.get('category', None)
    if category_id:
        try:
            category = DocumentCategory.objects.get(pk=category_id)
            # Include subcategories
            subcategories = DocumentCategory.objects.filter(parent=category)
            category_ids = [category.id] + [cat.id for cat in subcategories]
            queryset = queryset.filter(category__in=category_ids)
        except DocumentCategory.DoesNotExist:
            pass
    
    # Collection
    collection_id = request.query_params.get('collection', None)
    if collection_id:
        try:
            collection = DocumentCollection.objects.get(pk=collection_id)
            queryset = queryset.filter(collections=collection)
        except DocumentCollection.DoesNotExist:
            pass
    
    # Tags
    tags = request.query_params.get('tags', None)
    if tags:
        tag_list = tags.split(',')
        for tag in tag_list:
            queryset = queryset.filter(tags__name__in=[tag.strip()])
    
    # Date range (created_at)
    date_from = request.query_params.get('date_from', None)
    date_to = request.query_params.get('date_to', None)
    
    if date_from:
        try:
            date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
            # Add one day to include the end date
            date_to = date_to + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=date_to)
        except ValueError:
            pass
    
    # Uploaded by
    uploaded_by = request.query_params.get('uploaded_by', None)
    if uploaded_by:
        queryset = queryset.filter(uploaded_by__id=uploaded_by)
    
    # Is latest version
    latest_version = request.query_params.get('latest_version', None)
    if latest_version and latest_version.lower() == 'true':
        queryset = queryset.filter(is_latest_version=True)
    
    # Custom metadata
    metadata = request.query_params.get('metadata', None)
    if metadata:
        try:
            metadata_filters = json.loads(metadata)
            for field_id, value in metadata_filters.items():
                queryset = queryset.filter(
                    custom_metadata__field__id=field_id,
                    custom_metadata__value__icontains=value
                )
        except json.JSONDecodeError:
            pass
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))
    start = (page - 1) * page_size
    end = start + page_size
    
    # Ordering
    order_by = request.query_params.get('order_by', '-created_at')
    queryset = queryset.order_by(order_by)
    
    # Get total count
    total_count = queryset.count()
    
    # Apply pagination
    queryset = queryset[start:end]
    
    # Serialize and return
    serializer = DocumentSerializer(queryset, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def full_text_search(request):
    """Full-text search within document content"""
    search_text = request.query_params.get('q', None)
    if not search_text:
        return Response({"detail": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # This would use a search backend like Elasticsearch or Whoosh
    # For now, we'll just search in title and description
    queryset = Document.objects.filter(
        Q(title__icontains=search_text) | 
        Q(description__icontains=search_text) | 
        Q(keywords__icontains=search_text)
    )
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))
    start = (page - 1) * page_size
    end = start + page_size
    
    # Get total count
    total_count = queryset.count()
    
    # Apply pagination
    queryset = queryset[start:end]
    
    # Serialize and return
    serializer = DocumentSerializer(queryset, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recent_documents(request):
    """Get recent documents for the current user"""
    # Get documents uploaded by the user
    uploaded_docs = Document.objects.filter(
        uploaded_by=request.user
    ).order_by('-created_at')[:5]
    
    # Get documents in collections shared with the user
    shared_collections = DocumentCollection.objects.filter(
        shared_with=request.user
    )
    
    shared_docs = Document.objects.filter(
        collections__in=shared_collections
    ).exclude(
        uploaded_by=request.user
    ).order_by('-created_at')[:5]
    
    # Serialize and return
    uploaded_serializer = DocumentSerializer(uploaded_docs, many=True)
    shared_serializer = DocumentSerializer(shared_docs, many=True)
    
    return Response({
        'uploaded': uploaded_serializer.data,
        'shared': shared_serializer.data
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_suggestions(request):
    """Get document suggestions based on user's recent activity"""
    # This would be more sophisticated in a real implementation
    # For now, just return some documents with similar tags to the user's recent documents
    
    # Get user's recent documents
    recent_docs = Document.objects.filter(
        uploaded_by=request.user
    ).order_by('-created_at')[:3]
    
    # Get tags from recent documents
    tags = []
    for doc in recent_docs:
        tags.extend(doc.tags.names())
    
    # Find documents with similar tags
    suggested_docs = Document.objects.filter(
        tags__name__in=tags
    ).exclude(
        uploaded_by=request.user
    ).distinct().order_by('-created_at')[:5]
    
    # Serialize and return
    serializer = DocumentSerializer(suggested_docs, many=True)
    
    return Response(serializer.data)
