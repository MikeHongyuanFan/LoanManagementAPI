from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from datetime import date

from .models import Borrower
from .serializers import BorrowerSerializer
from applications.models import Application
from documents.models import Document
from notes.models import Note
from us_states import US_STATES

# REST API ViewSet
class BorrowerViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['state', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    ordering_fields = ['created_at', 'first_name', 'last_name']
    
    def create(self, request, *args, **kwargs):
        """
        Override to add additional validation
        """
        # Validate date of birth is not in the future
        if 'dob' in request.data:
            try:
                dob = date.fromisoformat(request.data['dob'])
                if dob > date.today():
                    return Response(
                        {"dob": "Date of birth cannot be in the future."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"dob": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Override to add additional validation
        """
        # Validate date of birth is not in the future
        if 'dob' in request.data:
            try:
                dob = date.fromisoformat(request.data['dob'])
                if dob > date.today():
                    return Response(
                        {"dob": "Date of birth cannot be in the future."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"dob": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().update(request, *args, **kwargs)

# HTML Views
@login_required
def borrower_list(request):
    """
    Display a list of borrowers with search and filtering
    """
    # Get search query
    search_query = request.GET.get('search', '')
    state_filter = request.GET.get('state', '')
    
    # Filter borrowers
    borrowers = Borrower.objects.all().order_by('-created_at')
    
    if search_query:
        borrowers = borrowers.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    if state_filter:
        borrowers = borrowers.filter(state=state_filter)
    
    # Check if JSON response is requested
    if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
        # Prepare data for JSON response
        borrowers_data = []
        for borrower in borrowers:
            borrowers_data.append({
                'id': borrower.id,
                'first_name': borrower.first_name,
                'last_name': borrower.last_name,
                'email': borrower.email,
                'phone_number': borrower.phone_number,
                'state': borrower.state,
                'dob': borrower.dob.isoformat() if borrower.dob else None,
                'repayment_account': borrower.repayment_account,
                'created_at': borrower.created_at.isoformat(),
                'updated_at': borrower.updated_at.isoformat(),
            })
        
        # Return JSON response
        return JsonResponse({
            'borrowers': borrowers_data,
            'total_count': borrowers.count(),
        })
    
    # Pagination for HTML response
    paginator = Paginator(borrowers, 10)  # Show 10 borrowers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Borrowers',
        'borrowers': page_obj,
        'page_obj': page_obj,
        'states': US_STATES,
    }
    
    return render(request, 'borrowers/list.html', context)

@login_required
def borrower_detail(request, pk):
    """
    Display detailed information about a borrower
    """
    borrower = get_object_or_404(Borrower, pk=pk)
    
    # Get related applications
    applications = Application.objects.filter(borrower=borrower).order_by('-created_at')
    
    # Get related documents
    documents = Document.objects.filter(borrower=borrower).order_by('-created_at')
    
    # Get notes
    notes = Note.objects.filter(
        content_type__model='borrower',
        object_id=borrower.id
    ).order_by('-created_at')
    
    # Check if JSON response is requested
    if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
        # Prepare data for JSON response
        borrower_data = {
            'id': borrower.id,
            'first_name': borrower.first_name,
            'last_name': borrower.last_name,
            'email': borrower.email,
            'phone_number': borrower.phone_number,
            'dob': borrower.dob.isoformat() if borrower.dob else None,
            'state': borrower.state,
            'repayment_account': borrower.repayment_account,
            'created_at': borrower.created_at.isoformat(),
            'updated_at': borrower.updated_at.isoformat(),
            'applications': [
                {
                    'id': app.id,
                    'product_name': app.product.name if app.product else None,
                    'gross_loan_amount': float(app.gross_loan_amount) if app.gross_loan_amount else 0,
                    'status': app.status,
                    'status_display': app.get_status_display(),
                    'stage': app.stage,
                    'stage_display': app.get_stage_display(),
                    'created_at': app.created_at.isoformat(),
                } for app in applications
            ],
            'documents': [
                {
                    'id': doc.id,
                    'name': doc.name,
                    'document_type': doc.document_type,
                    'document_type_display': doc.get_document_type_display(),
                    'status': doc.status,
                    'status_display': doc.get_status_display(),
                    'created_at': doc.created_at.isoformat(),
                } for doc in documents
            ],
            'notes': [
                {
                    'id': note.id,
                    'content': note.content,
                    'created_by': note.created_by.get_full_name() if note.created_by else None,
                    'created_at': note.created_at.isoformat(),
                } for note in notes
            ],
        }
        
        # Return JSON response
        return JsonResponse(borrower_data)
    
    context = {
        'title': f'{borrower.first_name} {borrower.last_name}',
        'borrower': borrower,
        'applications': applications,
        'documents': documents,
        'notes': notes,
    }
    
    return render(request, 'borrowers/detail.html', context)

@login_required
def borrower_create(request):
    """
    Create a new borrower
    """
    if request.method == 'POST':
        # Handle form submission
        data = request.POST.dict()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'phone_number', 'dob', 'state']
        for field in required_fields:
            if not data.get(field):
                messages.error(request, f'{field.replace("_", " ").title()} is required.')
                return redirect('borrower_create')
        
        # Create borrower
        try:
            borrower = Borrower.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone_number=data['phone_number'],
                dob=data['dob'],
                state=data['state'],
                repayment_account=data.get('repayment_account', '')
            )
            
            messages.success(request, f'Borrower {borrower.first_name} {borrower.last_name} created successfully.')
            
            # Check if there's a next parameter for redirection
            next_url = request.GET.get('next')
            if next_url:
                return redirect(f'{next_url}?borrower={borrower.id}')
            
            return redirect('borrower_detail', pk=borrower.id)
        except Exception as e:
            messages.error(request, f'Error creating borrower: {str(e)}')
            return redirect('borrower_create')
    
    # Check if JSON response is requested
    if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
        return JsonResponse({
            'states': dict(US_STATES),
        })
    
    context = {
        'title': 'Add Borrower',
        'states': US_STATES,
    }
    
    return render(request, 'borrowers/create.html', context)

@login_required
def borrower_edit(request, pk):
    """
    Edit an existing borrower
    """
    borrower = get_object_or_404(Borrower, pk=pk)
    
    if request.method == 'POST':
        # Handle form submission
        data = request.POST.dict()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'phone_number', 'dob', 'state']
        for field in required_fields:
            if not data.get(field):
                messages.error(request, f'{field.replace("_", " ").title()} is required.')
                return redirect('borrower_edit', pk=borrower.id)
        
        # Update borrower
        try:
            borrower.first_name = data['first_name']
            borrower.last_name = data['last_name']
            borrower.email = data['email']
            borrower.phone_number = data['phone_number']
            borrower.dob = data['dob']
            borrower.state = data['state']
            borrower.repayment_account = data.get('repayment_account', '')
            borrower.save()
            
            messages.success(request, f'Borrower {borrower.first_name} {borrower.last_name} updated successfully.')
            return redirect('borrower_detail', pk=borrower.id)
        except Exception as e:
            messages.error(request, f'Error updating borrower: {str(e)}')
            return redirect('borrower_edit', pk=borrower.id)
    
    # Check if JSON response is requested
    if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
        return JsonResponse({
            'borrower': {
                'id': borrower.id,
                'first_name': borrower.first_name,
                'last_name': borrower.last_name,
                'email': borrower.email,
                'phone_number': borrower.phone_number,
                'dob': borrower.dob.isoformat() if borrower.dob else None,
                'state': borrower.state,
                'repayment_account': borrower.repayment_account,
            },
            'states': dict(US_STATES),
        })
    
    context = {
        'title': f'Edit {borrower.first_name} {borrower.last_name}',
        'borrower': borrower,
        'states': US_STATES,
    }
    
    return render(request, 'borrowers/edit.html', context)

@login_required
def borrower_add_note(request, pk):
    """
    Add a note to a borrower
    """
    borrower = get_object_or_404(Borrower, pk=pk)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            note = Note.objects.create(
                content_object=borrower,
                content=content,
                created_by=request.user
            )
            
            # Check if JSON response is requested
            if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
                return JsonResponse({
                    'success': True,
                    'note': {
                        'id': note.id,
                        'content': note.content,
                        'created_by': note.created_by.get_full_name() if note.created_by else None,
                        'created_at': note.created_at.isoformat(),
                    }
                })
            
            messages.success(request, 'Note added successfully.')
        else:
            # Check if JSON response is requested
            if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
                return JsonResponse({
                    'success': False,
                    'error': 'Note content cannot be empty.'
                }, status=400)
            
            messages.error(request, 'Note content cannot be empty.')
    
    return redirect('borrower_detail', pk=borrower.id)

@login_required
def borrower_delete(request, pk):
    """
    Delete a borrower
    """
    borrower = get_object_or_404(Borrower, pk=pk)
    
    if request.method == 'POST':
        borrower_name = f"{borrower.first_name} {borrower.last_name}"
        borrower.delete()
        
        # Check if JSON response is requested
        if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
            return JsonResponse({
                'success': True,
                'message': f'Borrower {borrower_name} deleted successfully.'
            })
        
        messages.success(request, f'Borrower {borrower_name} deleted successfully.')
        return redirect('borrower_list')
    
    # Check if JSON response is requested for GET request
    if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
        return JsonResponse({
            'borrower': {
                'id': borrower.id,
                'first_name': borrower.first_name,
                'last_name': borrower.last_name,
            },
            'message': 'Use POST request to confirm deletion.'
        })
    
    return redirect('borrower_detail', pk=borrower.id)
