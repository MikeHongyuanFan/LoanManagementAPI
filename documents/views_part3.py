class CustomMetadataFieldViewSet(viewsets.ModelViewSet):
    """ViewSet for custom metadata fields"""
    queryset = CustomMetadataField.objects.all()
    serializer_class = CustomMetadataFieldSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['field_type', 'required', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def for_document_type(self, request):
        """Get metadata fields for a specific document type"""
        document_type = request.query_params.get('document_type')
        
        if not document_type:
            return Response({"error": "document_type parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        fields = CustomMetadataField.objects.filter(
            Q(document_types__isnull=True) | 
            Q(document_types__contains=[document_type])
        )
        
        serializer = self.get_serializer(fields, many=True)
        return Response(serializer.data)

class DocumentMetadataViewSet(viewsets.ModelViewSet):
    """ViewSet for document metadata"""
    queryset = DocumentMetadata.objects.all()
    serializer_class = DocumentMetadataSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document', 'field']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class DocumentRelationshipViewSet(viewsets.ModelViewSet):
    """ViewSet for document relationships"""
    queryset = DocumentRelationship.objects.all()
    serializer_class = DocumentRelationshipSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['source_document', 'target_document', 'relationship_type', 'created_by']
    search_fields = ['description', 'custom_type']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
