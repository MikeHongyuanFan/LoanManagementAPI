from rest_framework import permissions

class IsDocumentAccessible(permissions.BasePermission):
    """
    Custom permission to check if a document is accessible to the user.
    """
    
    def has_object_permission(self, request, view, obj):
        # Allow if user is the uploader
        if obj.uploaded_by == request.user:
            return True
            
        # Allow if user has appropriate access level
        if request.user.is_authenticated:
            # Admins can access all documents
            if request.user.is_staff or request.user.is_superuser:
                return True
                
            # Check if document is in a shared collection
            shared_collections = obj.collections.filter(is_shared=True)
            if shared_collections.exists():
                return True
                
            # Check if document is shared with user
            user_collections = obj.collections.filter(shared_with=request.user)
            if user_collections.exists():
                return True
                
        # Public documents (access_level=1) are accessible to all
        if obj.access_level == 1:
            return True
            
        # Otherwise deny access
        return False
