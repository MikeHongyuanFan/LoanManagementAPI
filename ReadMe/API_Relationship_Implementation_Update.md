# API Relationship Implementation Update

This document outlines the implementation of missing API relationships identified during our validation process.

## 1. Notification Relationships for Document Workflows

### Implemented Features

We have successfully implemented notification triggers for document approval and signature request workflows:

1. **Document Approval Notifications**
   - Notification sent to reviewer when approval is requested
   - Notification sent to requester when document is approved or rejected
   - Notification sent to new reviewer when approval is reassigned

2. **Signature Request Notifications**
   - Notification sent to signer when signature is requested
   - Notification sent to requester when document is signed or declined

### Implementation Details

1. **Created Notification Service Layer**
   - Implemented a dedicated service module (`notifications/services.py`) for notification creation
   - Created specialized functions for document workflow notifications:
     - `create_document_approval_notification()`
     - `create_signature_request_notification()`

2. **Integrated Notifications in Document Approval Workflow**
   - Added notification triggers in `request_document_approval` function
   - Added notification triggers in `respond_to_approval` function
   - Added notification triggers in `reassign_approval` function

3. **Integrated Notifications in Signature Request Workflow**
   - Added notification triggers in `signature_request_respond` function
   - Added notification triggers in `request_signature` action in DocumentViewSet

### Code Structure

```python
# notifications/services.py
def create_document_approval_notification(approval):
    """
    Create notification for document approval events
    """
    # Implementation for different approval statuses:
    # - pending: notify reviewer
    # - approved/rejected: notify requester
    # - reassigned: notify new reviewer

def create_signature_request_notification(signature_request):
    """
    Create notification for signature request events
    """
    # Implementation for different signature request statuses:
    # - pending: notify signer
    # - signed/declined: notify requester
```

## 2. Document Relationship Management

### Implemented Features

We have successfully implemented document relationship management endpoints:

1. **Document-Centric Relationship Endpoints**
   - `/api/document-management/documents/{id}/add-relationship/` - Add a relationship from a document to another document
   - `/api/document-management/documents/{id}/remove-relationship/` - Remove a relationship from a document
   - `/api/document-management/documents/{id}/relationships/` - Get all relationships for a document (both incoming and outgoing)

2. **Relationship-Centric Endpoints**
   - `/api/document-management/relationships/add/` - Add a relationship between any two documents
   - `/api/document-management/relationships/{id}/remove/` - Remove a specific relationship

### Implementation Details

1. **Enhanced DocumentViewSet**
   - Added `add_relationship` action for creating relationships from a specific document
   - Added `remove_relationship` action for removing relationships from a specific document
   - Added `relationships` action for retrieving all relationships for a document

2. **Enhanced DocumentRelationshipViewSet**
   - Added `add_relationship` action for creating relationships between any two documents
   - Added `remove_relationship` action for removing specific relationships

3. **Comprehensive Validation**
   - Validation for required fields (source document, target document, relationship type)
   - Validation for relationship types with custom type handling
   - Duplicate relationship checking
   - Permission checking for relationship deletion

### Code Structure

```python
# DocumentViewSet relationship actions
@action(detail=True, methods=['post'])
def add_relationship(self, request, pk=None):
    """Add a relationship from this document to another document"""
    # Implementation for creating a relationship from the current document

@action(detail=True, methods=['post'])
def remove_relationship(self, request, pk=None):
    """Remove a relationship from this document to another document"""
    # Implementation for removing a relationship from the current document

@action(detail=True, methods=['get'])
def relationships(self, request, pk=None):
    """Get all relationships for this document (both source and target)"""
    # Implementation for retrieving all relationships for the current document

# DocumentRelationshipViewSet relationship actions
@action(detail=False, methods=['post'])
def add_relationship(self, request):
    """Add a relationship between two documents"""
    # Implementation for creating a relationship between any two documents

@action(detail=True, methods=['delete'])
def remove_relationship(self, request, pk=None):
    """Remove a relationship between documents"""
    # Implementation for removing a specific relationship
```

### URL Configuration

```python
# Document relationship endpoints
path('documents/<int:pk>/add-relationship/', views.DocumentViewSet.as_view({'post': 'add_relationship'}), name='document-add-relationship'),
path('documents/<int:pk>/remove-relationship/', views.DocumentViewSet.as_view({'post': 'remove_relationship'}), name='document-remove-relationship'),
path('documents/<int:pk>/relationships/', views.DocumentViewSet.as_view({'get': 'relationships'}), name='document-relationships'),
path('relationships/add/', views.DocumentRelationshipViewSet.as_view({'post': 'add_relationship'}), name='add-relationship'),
path('relationships/<int:pk>/remove/', views.DocumentRelationshipViewSet.as_view({'delete': 'remove_relationship'}), name='remove-relationship'),
```

## 3. Calculator Relationship Improvements

### Implemented Features

We have successfully improved the calculator component relationships:

1. **Enhanced Model Relationships**
   - Added direct relationship between `LoanCalculation` and `Product` models
   - Added direct relationship between `ApplicationFee` and `LoanCalculation` models
   - Added related_name attributes to improve reverse relationship access

2. **Comprehensive Documentation**
   - Created detailed documentation of calculator component relationships
   - Documented both direct model relationships and business logic connections
   - Created a data flow diagram showing the relationships between components

### Implementation Details

1. **Model Enhancements**
   - Added `product` field to `LoanCalculation` model:
     ```python
     product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='calculations', null=True)
     ```
   - Added `calculation` field to `ApplicationFee` model:
     ```python
     calculation = models.ForeignKey(LoanCalculation, on_delete=models.SET_NULL, related_name='fees', null=True)
     ```
   - Added related_name to `Fee` model's relationship with `ApplicationFee`:
     ```python
     fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name='application_fees')
     ```

2. **View Logic Updates**
   - Updated the calculation view to store the product reference
   - Updated the fee creation logic to store the calculation reference

3. **Documentation**
   - Created comprehensive documentation in `ReadMe/CALCULATOR_RELATIONSHIPS.md`
   - Documented direct model relationships
   - Documented business logic connections
   - Created a data flow diagram
   - Documented API integration points

### Documentation Excerpt

```markdown
## Model Relationships

### Direct Model Relationships

The calculator module includes the following direct model relationships:

1. **LoanCalculation → Application**
   - One-to-one relationship: Each loan calculation is associated with exactly one application
   - Relationship field: `application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='calculation')`
   - This allows easy access to calculation data from an application: `application.calculation`

2. **LoanCalculation → Product**
   - Many-to-one relationship: Each loan calculation is associated with one product
   - Relationship field: `product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='calculations', null=True)`
   - This allows tracking which product was used for the calculation
   - The relationship is nullable to handle cases where the product is deleted

...

## Business Logic Connections

Beyond direct model relationships, there are several important business logic connections between calculator components:

### 1. Calculation Flow

The calculation flow connects various components in the following sequence:

```
User Input → LoanCalculation → RepaymentSchedule → ApplicationFee → Total Cost
```
```

## Conclusion

We have successfully implemented all three of the key missing relationships identified in our API validation:

1. **Notification triggers for document workflows** - Ensuring users are properly notified of important events in the document approval and signature workflows.

2. **Document relationship management endpoints** - Providing comprehensive API support for creating, managing, and retrieving relationships between documents.

3. **Calculator component relationship improvements** - Enhancing the direct model relationships between calculator components and documenting the business logic connections.

These enhancements significantly improve the system's functionality, maintainability, and documentation, addressing all the gaps identified in our API relationship validation.
