class DocumentCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for document comments"""
    queryset = DocumentComment.objects.all()
    serializer_class = DocumentCommentSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'user']
    ordering_fields = ['created_at']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DocumentApprovalViewSet(viewsets.ModelViewSet):
    """ViewSet for document approvals"""
    queryset = DocumentApproval.objects.all()
    serializer_class = DocumentApprovalSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'reviewer', 'status', 'requested_by']
    ordering_fields = ['requested_date']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a document"""
        approval = self.get_object()
        comments = request.data.get('comments', '')
        
        if approval.status != 'pending':
            return Response({"error": "This approval is not pending"}, status=status.HTTP_400_BAD_REQUEST)
        
        approval.status = 'approved'
        approval.comments = comments
        approval.response_date = timezone.now()
        approval.save()
        
        # Update document status if all approvals are complete
        document = approval.document
        pending_approvals = document.approvals.filter(status='pending').count()
        
        if pending_approvals == 0:
            document.status = 'approved'
            document.save()
        
        serializer = self.get_serializer(approval)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a document"""
        approval = self.get_object()
        comments = request.data.get('comments', '')
        
        if approval.status != 'pending':
            return Response({"error": "This approval is not pending"}, status=status.HTTP_400_BAD_REQUEST)
        
        approval.status = 'rejected'
        approval.comments = comments
        approval.response_date = timezone.now()
        approval.save()
        
        # Update document status
        document = approval.document
        document.status = 'rejected'
        document.save()
        
        serializer = self.get_serializer(approval)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reassign(self, request, pk=None):
        """Reassign approval to another reviewer"""
        approval = self.get_object()
        new_reviewer_id = request.data.get('reviewer_id')
        
        if not new_reviewer_id:
            return Response({"error": "reviewer_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if approval.status != 'pending':
            return Response({"error": "Only pending approvals can be reassigned"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_reviewer = User.objects.get(id=new_reviewer_id)
            approval.reviewer = new_reviewer
            approval.save()
            
            serializer = self.get_serializer(approval)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "Reviewer not found"}, status=status.HTTP_404_NOT_FOUND)
