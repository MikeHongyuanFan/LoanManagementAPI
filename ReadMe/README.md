# CRM Loan Management System

A comprehensive loan management system built with Django and MySQL, designed to handle the entire loan application lifecycle from submission to approval and management.

## Project Overview

This CRM Loan Management System is designed to manage:
- Loan applications and their lifecycle
- Borrower and broker information
- Document management
- Loan calculations and financial modules
- Notifications and reminders

## Development Status

Current development status: **Phase 4 Complete**

- ✅ Phase 1: Basic Framework & Setup
- ✅ Phase 2: API Development
- ✅ Phase 3: Loan Calculator Implementation
- ✅ Phase 4: Document Management System
  - ⏳ Some advanced search features pending (full-text search)
- ⏳ Phase 5: Notification System (Upcoming)
- ⏳ Phase 6: User Interface Enhancement (Upcoming)
- ⏳ Phase 7: Testing, QA, and Deployment (Upcoming)

## Documentation

- [PROJECT_PLAN.md](PROJECT_PLAN.md) - Project plan and implementation details
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation and usage examples

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL 5.7+ (SQLite for development)
- pip

### Installation

1. Clone the repository:
```
git clone <repository-url>
cd LoanApplicationBackend
```

2. Create a virtual environment:
```
python -m venv venv
```

3. Activate the virtual environment:
```
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Configure the database in `settings.py`

6. Run migrations:
```
python manage.py makemigrations
python manage.py migrate
```

7. Create a superuser:
```
python manage.py createsuperuser
```

8. Run the development server:
```
python manage.py runserver
```

## Project Structure

```
LoanApplicationBackend/
├── loan_management/          # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── applications/             # Loan applications app
├── borrowers/                # Borrowers management app
├── brokers/                  # Brokers management app
├── products/                 # Products configuration app
├── calculator/               # Loan calculator app
├── documents/                # Document management app
├── notifications/            # Notification system app
├── users/                    # User authentication app
├── templates/                # HTML templates
├── static/                   # Static files (CSS, JS)
├── media/                    # User-uploaded files
├── manage.py                 # Django management script
├── README.md                 # This file
├── PROJECT_PLAN.md           # Project plan and implementation details
├── API_REFERENCE.md          # API documentation
└── requirements.txt          # Project dependencies
```

## Testing

Run tests with:
```
python manage.py test
```

## License

[License information]
