class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for document templates"""
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['template_type', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

class DocumentCollectionViewSet(viewsets.ModelViewSet):
    """ViewSet for document collections"""
    queryset = DocumentCollection.objects.all()
    serializer_class = DocumentCollectionSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_by', 'is_shared', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        """Filter collections based on user"""
        user = self.request.user
        if user.is_authenticated:
            return DocumentCollection.objects.filter(
                Q(created_by=user) | Q(is_shared=True) | Q(shared_with=user)
            ).distinct()
        return DocumentCollection.objects.filter(is_shared=True)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def subcollections(self, request, pk=None):
        """Get all subcollections of a collection"""
        collection = self.get_object()
        subcollections = DocumentCollection.objects.filter(parent=collection)
        serializer = self.get_serializer(subcollections, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get all documents in a collection"""
        collection = self.get_object()
        documents = collection.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share a collection with users"""
        collection = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        if not user_ids:
            return Response({"error": "No user IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        collection.is_shared = True
        collection.save()
        
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                collection.shared_with.add(user)
            except User.DoesNotExist:
                pass
        
        serializer = self.get_serializer(collection)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unshare(self, request, pk=None):
        """Unshare a collection with users"""
        collection = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        if not user_ids:
            # Unshare with everyone
            collection.is_shared = False
            collection.shared_with.clear()
        else:
            # Unshare with specific users
            for user_id in user_ids:
                try:
                    user = User.objects.get(id=user_id)
                    collection.shared_with.remove(user)
                except User.DoesNotExist:
                    pass
            
            # If no more shared users, set is_shared to False
            if collection.shared_with.count() == 0:
                collection.is_shared = False
        
        collection.save()
        serializer = self.get_serializer(collection)
        return Response(serializer.data)
