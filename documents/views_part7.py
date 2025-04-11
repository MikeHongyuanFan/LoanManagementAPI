class DocumentSignatureRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for document signature requests"""
    queryset = DocumentSignatureRequest.objects.all()
    serializer_class = DocumentSignatureRequestSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'signer', 'status', 'requested_by']
    ordering_fields = ['requested_date', 'due_date']
    
    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """Sign a document"""
        signature_request = self.get_object()
        signature_type = request.data.get('signature_type', 'typed')
        signature_data = request.data.get('signature_data', '')
        
        if signature_request.status not in ['pending', 'viewed']:
            return Response({"error": "This signature request cannot be signed"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not signature_data:
            return Response({"error": "signature_data is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create signature
        signature = DocumentSignature.objects.create(
            signature_request=signature_request,
            document=signature_request.document,
            signer=signature_request.signer,
            signature_type=signature_type,
            signature_data=signature_data,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            verification_hash=self.generate_verification_hash(signature_request, signature_data)
        )
        
        # Update signature request status
        signature_request.status = 'signed'
        signature_request.response_date = timezone.now()
        signature_request.save()
        
        # Update document status
        document = signature_request.document
        pending_signatures = document.signature_requests.filter(status__in=['pending', 'viewed']).count()
        
        if pending_signatures == 0:
            document.status = 'signed'
            document.save()
        
        serializer = DocumentSignatureSerializer(signature)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline to sign a document"""
        signature_request = self.get_object()
        decline_reason = request.data.get('reason', '')
        
        if signature_request.status not in ['pending', 'viewed']:
            return Response({"error": "This signature request cannot be declined"}, status=status.HTTP_400_BAD_REQUEST)
        
        signature_request.status = 'declined'
        signature_request.decline_reason = decline_reason
        signature_request.response_date = timezone.now()
        signature_request.save()
        
        # Update document status
        document = signature_request.document
        document.status = 'signature_declined'
        document.save()
        
        serializer = self.get_serializer(signature_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a signature request"""
        signature_request = self.get_object()
        
        if signature_request.status not in ['pending', 'viewed']:
            return Response({"error": "This signature request cannot be cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        
        signature_request.status = 'cancelled'
        signature_request.response_date = timezone.now()
        signature_request.save()
        
        serializer = self.get_serializer(signature_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_viewed(self, request, pk=None):
        """Mark a signature request as viewed"""
        signature_request = self.get_object()
        
        if signature_request.status != 'pending':
            return Response({"error": "Only pending signature requests can be marked as viewed"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        signature_request.status = 'viewed'
        signature_request.viewed_date = timezone.now()
        signature_request.save()
        
        serializer = self.get_serializer(signature_request)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def generate_verification_hash(self, signature_request, signature_data):
        """Generate a verification hash for the signature"""
        import hashlib
        import time
        
        # Create a unique hash based on document, signer, timestamp, and signature data
        data = f"{signature_request.document.id}:{signature_request.signer.id}:{time.time()}:{signature_data}"
        return hashlib.sha256(data.encode()).hexdigest()
