# CRM Loan Management System

This is a comprehensive loan management system built with Django and Django REST Framework.

## Features

- Loan application management
- Document management with versioning and electronic signatures
- Full-text search for document content
- Borrower and broker management
- Loan product configuration
- Loan calculator with amortization schedules
- Notification system

## New Feature: Full-Text Search for Document Content

We've implemented full-text search for document content using Django Haystack with Whoosh as the search backend and textract for content extraction. This allows users to search within the content of uploaded documents (PDF, DOCX, etc.) in addition to document metadata.

### Search Features

- Search within document content
- Filter by document type, status, and date range
- Sort results by various fields
- Pagination of search results

### API Endpoint

```
GET /api/document-management/search/?q=search_term
```

Optional parameters:
- `document_type`: Filter by document type
- `status`: Filter by document status
- `date_from`: Filter by creation date (from)
- `date_to`: Filter by creation date (to)
- `ordering`: Sort results (e.g., `-created_at` for newest first)

### Example Request

```
GET /api/document-management/search/?q=mortgage&document_type=agreement&status=approved&ordering=-created_at
```

### Example Response

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 123,
      "title": "Mortgage Agreement",
      "description": "Standard mortgage agreement",
      "document_type": "agreement",
      "status": "approved",
      "created_at": "2025-04-10T10:30:00Z",
      "updated_at": "2025-04-10T10:30:00Z"
    },
    {
      "id": 124,
      "title": "Refinance Agreement",
      "description": "Mortgage refinance agreement",
      "document_type": "agreement",
      "status": "approved",
      "created_at": "2025-04-09T14:15:00Z",
      "updated_at": "2025-04-09T14:15:00Z"
    }
  ],
  "query": "mortgage"
}
```

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Build the search index: `python manage.py rebuild_document_index`
7. Create a superuser: `python manage.py createsuperuser`
8. Run the development server: `python manage.py runserver`

## Dependencies

- Django 4.2+
- Django REST Framework
- Django Haystack
- Whoosh
- textract (for document content extraction)
- PyPDF2
- And more (see requirements.txt)

## API Documentation

See API_REFERENCE.md for detailed API documentation.
