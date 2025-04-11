class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for documents"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'category', 'status', 'application', 'is_confidential', 'is_favorite', 'is_pinned']
    search_fields = ['title', 'description', 'keywords']
    ordering_fields = ['title', 'created_at', 'updated_at', 'status']
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_to_collection(self, request, pk=None):
        """Add document to a collection"""
        document = self.get_object()
        collection_id = request.data.get('collection_id')
        
        if not collection_id:
            return Response({"error": "collection_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            collection = DocumentCollection.objects.get(id=collection_id)
            document.collections.add(collection)
            return Response({"status": "Document added to collection"})
        except DocumentCollection.DoesNotExist:
            return Response({"error": "Collection not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_from_collection(self, request, pk=None):
        """Remove document from a collection"""
        document = self.get_object()
        collection_id = request.data.get('collection_id')
        
        if not collection_id:
            return Response({"error": "collection_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            collection = DocumentCollection.objects.get(id=collection_id)
            document.collections.remove(collection)
            return Response({"status": "Document removed from collection"})
        except DocumentCollection.DoesNotExist:
            return Response({"error": "Collection not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status of a document"""
        document = self.get_object()
        document.is_favorite = not document.is_favorite
        document.save()
        return Response({"is_favorite": document.is_favorite})
    
    @action(detail=True, methods=['post'])
    def toggle_pinned(self, request, pk=None):
        """Toggle pinned status of a document"""
        document = self.get_object()
        document.is_pinned = not document.is_pinned
        document.save()
        return Response({"is_pinned": document.is_pinned})
