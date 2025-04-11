class DocumentSignatureViewSet(viewsets.ModelViewSet):
    """ViewSet for document signatures"""
    queryset = DocumentSignature.objects.all()
    serializer_class = DocumentSignatureSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'signer', 'signature_type']
    ordering_fields = ['signature_date']
    
    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        """Verify a signature"""
        signature = self.get_object()
        
        verification_data = {
            'signature_id': signature.id,
            'document_id': signature.document.id,
            'document_title': signature.document.title,
            'signer': {
                'id': signature.signer.id,
                'name': f"{signature.signer.first_name} {signature.signer.last_name}",
                'email': signature.signer.email
            },
            'signature_type': signature.signature_type,
            'signature_date': signature.signature_date,
            'ip_address': signature.ip_address,
            'user_agent': signature.user_agent,
            'is_valid': True,  # In a real system, you would verify the hash here
            'verification_hash': signature.verification_hash
        }
        
        return Response(verification_data)
