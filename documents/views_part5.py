    @action(detail=True, methods=['post'])
    def add_metadata(self, request, pk=None):
        """Add custom metadata to a document"""
        document = self.get_object()
        field_id = request.data.get('field_id')
        value = request.data.get('value')
        
        if not field_id or value is None:
            return Response({"error": "field_id and value are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            field = CustomMetadataField.objects.get(id=field_id)
            
            # Check if metadata already exists for this field
            metadata, created = DocumentMetadata.objects.update_or_create(
                document=document,
                field=field,
                defaults={
                    'value': value,
                    'created_by': request.user
                }
            )
            
            serializer = DocumentMetadataSerializer(metadata)
            return Response(serializer.data)
        except CustomMetadataField.DoesNotExist:
            return Response({"error": "Metadata field not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def add_relationship(self, request, pk=None):
        """Add a relationship to another document"""
        source_document = self.get_object()
        target_document_id = request.data.get('target_document_id')
        relationship_type = request.data.get('relationship_type')
        custom_type = request.data.get('custom_type')
        description = request.data.get('description')
        
        if not target_document_id or not relationship_type:
            return Response({"error": "target_document_id and relationship_type are required"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        if relationship_type == 'custom' and not custom_type:
            return Response({"error": "custom_type is required for custom relationship_type"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_document = Document.objects.get(id=target_document_id)
            
            # Check if relationship already exists
            relationship, created = DocumentRelationship.objects.get_or_create(
                source_document=source_document,
                target_document=target_document,
                relationship_type=relationship_type,
                defaults={
                    'custom_type': custom_type,
                    'description': description,
                    'created_by': request.user
                }
            )
            
            if not created:
                return Response({"error": "Relationship already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = DocumentRelationshipSerializer(relationship)
            return Response(serializer.data)
        except Document.DoesNotExist:
            return Response({"error": "Target document not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def relationships(self, request, pk=None):
        """Get all relationships for a document"""
        document = self.get_object()
        related_docs = document.get_related_documents()
        
        return Response(related_docs)
