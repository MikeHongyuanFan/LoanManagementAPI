# CRM Loan Management System

A comprehensive loan management system built with Django and Django REST Framework, designed to handle the entire loan application lifecycle from submission to approval and management.

## Project Overview

The CRM Loan Management System provides a robust platform for financial institutions to manage their loan operations efficiently. The system is built with a focus on document management, workflow automation, and comprehensive API support.

### Key Features

- **Loan Application Processing**
  - Complete application lifecycle management
  - Status and stage tracking
  - Application duplication
  - Supporting entities (valuers, quantity surveyors, referrals)

- **Advanced Document Management**
  - Document versioning with comparison and rollback
  - Electronic signature integration
  - Full-text search within document content
  - Hierarchical document organization
  - Document relationships and metadata
  - Multi-step approval workflows

- **Borrower and Broker Management**
  - Comprehensive profile management
  - Document association
  - Application history tracking

- **Loan Product Configuration**
  - Flexible product definition
  - Interest rates and terms
  - Fee structures
  - Eligibility criteria

- **Loan Calculator**
  - Amortization schedules
  - Interest-only calculations
  - Fee calculations
  - Total cost analysis

- **Notification System**
  - System notifications
  - Email notifications
  - User-specific notifications
  - Notes and reminders

## Development Status

Current development status: **Phase 2 Complete**

- ✅ **Phase 1: Core Features** (Completed)
  - User authentication and authorization
  - Borrower management
  - Loan application processing
  - Loan product configuration
  - Basic document management
  - Notification system

- ✅ **Phase 2: Advanced Document Management** (Completed)
  - Document versioning with comparison and rollback
  - Enhanced approval workflow with multi-step processes
  - Notification system integration
  - Electronic signature integration
  - Full-text search for document content
  - Advanced document organization features

- 🔄 **Phase 3: Loan Servicing** (Planned)
  - Payment tracking and processing (manual implementation)
  - Late payment management
  - Interest calculation
  - Payment reminders and notifications
  - Payment history and reporting

- 🔄 **Phase 4: Reporting and Analytics** (Planned)
  - Dashboard with key metrics
  - Custom report generation
  - Data visualization
  - Export functionality
  - Scheduled reports

- 🔄 **Phase 5: Integrations** (Planned)
  - Document OCR and data extraction
  - Optional third-party integrations

## System Architecture

### Backend
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Search Engine**: Django Haystack with Whoosh
- **Document Processing**: textract, PyPDF2
- **Authentication**: JWT, OAuth2

### Deployment
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions

## API Structure

The system provides a comprehensive set of RESTful APIs:

- **Document Management APIs**: CRUD operations, versioning, workflows, signatures
- **Loan Application APIs**: Application processing, status transitions
- **Borrower and Broker APIs**: Profile management, search
- **Calculator APIs**: Loan calculations, repayment schedules
- **Notification APIs**: Notification management, notes
- **Product APIs**: Product configuration, fee structure

For detailed API documentation, see [ReadMe/API_REFERENCE.md](ReadMe/API_REFERENCE.md).

## Project Structure

```
LoanApplicationBackend/
├── loan_management/          # Main Django project
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL routing
│   └── wsgi.py               # WSGI configuration
├── applications/             # Loan applications app
│   ├── models.py             # Application data models
│   ├── serializers.py        # API serializers
│   ├── views.py              # API views
│   └── urls.py               # URL routing
├── borrowers/                # Borrowers management app
├── brokers/                  # Brokers management app
├── products/                 # Products configuration app
├── calculator/               # Loan calculator app
├── documents/                # Document management app
│   ├── models/               # Document models
│   │   ├── document.py       # Core document model
│   │   ├── category.py       # Document categories
│   │   ├── collection.py     # Document collections
│   │   ├── relationship.py   # Document relationships
│   │   ├── metadata.py       # Custom metadata
│   │   ├── approval.py       # Approval workflow
│   │   └── signature.py      # Electronic signatures
│   ├── serializers/          # API serializers
│   ├── views/                # API views
│   ├── services/             # Business logic
│   ├── permissions.py        # Custom permissions
│   └── urls.py               # URL routing
├── notifications/            # Notification system app
├── users/                    # User authentication app
├── utils/                    # Utility functions and helpers
├── templates/                # HTML templates
├── static/                   # Static files (CSS, JS)
├── media/                    # User-uploaded files
├── tests/                    # Test suite
├── ReadMe/                   # Documentation
│   ├── API_REFERENCE.md      # Complete API reference
│   ├── ADVANCED_DOCUMENT_ORGANIZATION.md # Document features
│   ├── ORGANIZATION.md       # Documentation guide
│   ├── alternative_payment_tracking.md   # Payment tracking
│   └── payment_verification_plan.md      # Payment verification
├── manage.py                 # Django management script
├── requirements.txt          # Project dependencies
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
└── .github/                  # GitHub Actions workflows
```

## Dependencies

### Core Dependencies
- Django 4.2+
- Django REST Framework 3.14+
- djangorestframework-simplejwt
- django-filter
- django-cors-headers

### Database
- psycopg2-binary (PostgreSQL)

### Document Processing
- Django Haystack
- Whoosh
- textract
- PyPDF2
- python-magic
- pdf2image
- Pillow

### Testing
- pytest
- pytest-django
- factory_boy
- coverage

### Development Tools
- black (code formatting)
- flake8 (linting)
- isort (import sorting)
- pre-commit

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ (for production) or SQLite (for development)
- pip
- virtualenv or venv

### Installation

1. Clone the repository:
```bash
git clone https://github.com/MikeHongyuanFan/LoanManagementAPI.git
cd LoanApplicationBackend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure the database in `loan_management/settings.py`:
```python
# For development (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# For production (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'loan_management',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

6. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Build the search index:
```bash
python manage.py rebuild_document_index
```

8. Create a superuser:
```bash
python manage.py createsuperuser
```

9. Run the development server:
```bash
python manage.py runserver
```

### Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Run migrations in Docker:
```bash
docker-compose exec web python manage.py migrate
```

3. Create a superuser in Docker:
```bash
docker-compose exec web python manage.py createsuperuser
```

## Testing

Run the test suite:
```bash
# Run all tests
python manage.py test

# Run with pytest
pytest

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Documentation

- [ReadMe/API_REFERENCE.md](ReadMe/API_REFERENCE.md) - Complete API reference
- [ReadMe/ADVANCED_DOCUMENT_ORGANIZATION.md](ReadMe/ADVANCED_DOCUMENT_ORGANIZATION.md) - Document management features
- [ReadMe/ORGANIZATION.md](ReadMe/ORGANIZATION.md) - Documentation guide
- [ReadMe/alternative_payment_tracking.md](ReadMe/alternative_payment_tracking.md) - Alternative payment tracking approach
- [ReadMe/payment_verification_plan.md](ReadMe/payment_verification_plan.md) - Payment verification plan

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please contact the project maintainers:
- Mike Fan - <email@example.com>
