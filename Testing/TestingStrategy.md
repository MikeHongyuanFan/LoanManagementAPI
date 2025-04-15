# 🧪 Django Backend Testing Strategy

A structured and progressive testing approach for Django-based backend systems, covering everything from core functionality to security and performance.

---

## ✅ Stage 1: Functional Testing

**Purpose:**  
Verify that each individual API endpoint or view functions as intended under normal conditions.

**What to cover:**
- API endpoints return correct status codes and payloads.
- CRUD operations behave as expected.
- Response structure and fields are correct.
- HTTP methods are properly handled.

**Example Test:**
```python
def test_list_documents(self):
    """Test that the documents list endpoint returns 200 and correct data structure."""
    self.client.force_authenticate(user=self.user)
    response = self.client.get('/api/document-management/documents/')
    self.assertEqual(response.status_code, 200)
    self.assertIn('results', response.data)
    self.assertIn('count', response.data)
```

---

## 🧱 Stage 2: Input Validation & Error Handling

**Purpose:**  
Ensure that the system handles bad or malformed input safely and consistently.

**What to cover:**
- Required fields and data types are enforced.
- Invalid inputs trigger proper 400-series responses.
- Business rule violations return meaningful error messages.
- Inputs at boundary conditions (e.g., string length, max values).

**Example Test:**
```python
def test_create_document_missing_required_field(self):
    """Test that creating a document without a required field returns 400."""
    self.client.force_authenticate(user=self.user)
    data = {
        'description': 'Test document',
        # Missing required 'title' field
    }
    response = self.client.post('/api/document-management/documents/', data)
    self.assertEqual(response.status_code, 400)
    self.assertIn('title', response.data)  # Error message for missing field
```

---

## 🔐 Stage 3: Authentication & Authorization

**Purpose:**  
Confirm that only properly authenticated and authorized users can access protected routes and perform sensitive operations.

**What to cover:**
- Login and token authentication flows.
- Access to restricted routes based on user roles.
- Token expiration and refresh scenarios.
- Attempted unauthorized access returns 401/403.

**Example Test:**
```python
def test_document_access_unauthorized(self):
    """Test that unauthenticated users cannot access documents."""
    # No authentication
    response = self.client.get('/api/document-management/documents/')
    self.assertEqual(response.status_code, 401)
    
def test_document_permission_denied(self):
    """Test that users cannot access documents they don't have permission for."""
    self.client.force_authenticate(user=self.regular_user)
    response = self.client.get(f'/api/document-management/documents/{self.confidential_doc.id}/')
    self.assertEqual(response.status_code, 403)
```

---

## 🧬 Stage 4: Model Logic Testing

**Purpose:**  
Verify that model-level logic and relationships work correctly.

**What to cover:**
- Custom model methods and business logic.
- Model constraints, defaults, and validations.
- Field types and behaviors.
- Relationship integrity (ForeignKey, ManyToMany, etc.).

**Example Test:**
```python
def test_document_version_increment(self):
    """Test that document version increments correctly when updated."""
    doc = Document.objects.create(title="Test Doc", created_by=self.user)
    initial_version = doc.version
    doc.update_content("New content")
    doc.refresh_from_db()
    self.assertEqual(doc.version, initial_version + 1)
    
def test_document_category_relationship(self):
    """Test document-category relationship."""
    category = DocumentCategory.objects.create(name="Test Category")
    doc = Document.objects.create(
        title="Test Doc", 
        created_by=self.user,
        category=category
    )
    self.assertEqual(doc.category.name, "Test Category")
    self.assertIn(doc, category.documents.all())
```

---

## 🧾 Stage 5: Serializer Testing

**Purpose:**  
Validate data transformation and validation using Django REST Framework serializers.

**What to cover:**
- Serialization of model instances to JSON.
- Deserialization and validation of input data.
- Custom field handling and error messages.
- Read/write field behavior and nested relationships.

**Example Test:**
```python
def test_document_serializer_validation(self):
    """Test document serializer validation."""
    serializer = DocumentSerializer(data={
        'title': 'A' * 300,  # Exceeds max length
        'document_type': 'invalid_type'  # Not in choices
    })
    self.assertFalse(serializer.is_valid())
    self.assertIn('title', serializer.errors)
    self.assertIn('document_type', serializer.errors)
    
def test_document_serializer_nested_data(self):
    """Test serialization with nested relationships."""
    doc = Document.objects.create(title="Test Doc", created_by=self.user)
    serializer = DocumentDetailSerializer(doc)
    self.assertIn('created_by', serializer.data)
    self.assertEqual(serializer.data['created_by']['username'], self.user.username)
```

---

## 🌐 Stage 6: URL Routing & Reverse Resolution

**Purpose:**  
Ensure that all URL patterns route to the correct views or viewsets.

**What to cover:**
- All named routes resolve properly.
- URLs handle path parameters correctly.
- Invalid URLs result in 404s.
- Reversing URLs with `reverse()` produces correct results.

**Example Test:**
```python
def test_document_detail_url_resolution(self):
    """Test that document detail URL resolves correctly."""
    url = reverse('document-detail', kwargs={'pk': 1})
    self.assertEqual(url, '/api/document-management/documents/1/')
    
def test_invalid_url_returns_404(self):
    """Test that invalid URLs return 404."""
    self.client.force_authenticate(user=self.user)
    response = self.client.get('/api/document-management/invalid-endpoint/')
    self.assertEqual(response.status_code, 404)
```

---

## 🔄 Stage 7: Integration Testing

**Purpose:**  
Test the interaction between multiple components (views, serializers, models) in complete flows.

**What to cover:**
- Multi-step workflows across endpoints.
- DB write-read consistency.
- Combined behavior of views, permissions, serializers.
- Side effects like email sending or logging.

**Example Test:**
```python
def test_document_approval_workflow(self):
    """Test the complete document approval workflow."""
    # Create document
    self.client.force_authenticate(user=self.author)
    doc_response = self.client.post('/api/document-management/documents/', {
        'title': 'Document for Approval',
        'content': 'Test content'
    })
    doc_id = doc_response.data['id']
    
    # Submit for approval
    approval_response = self.client.post('/api/document-management/approvals/', {
        'document': doc_id,
        'reviewer': self.reviewer.id
    })
    approval_id = approval_response.data['id']
    
    # Reviewer approves
    self.client.force_authenticate(user=self.reviewer)
    approve_response = self.client.post(f'/api/document-management/approvals/{approval_id}/approve/', {
        'comments': 'Approved'
    })
    
    # Check document status updated
    doc = Document.objects.get(id=doc_id)
    self.assertEqual(doc.status, 'approved')
```

---

## 🚧 Stage 8: Edge Case & Boundary Testing

**Purpose:**  
Push the system to its edge cases to catch uncommon but critical issues.

**What to cover:**
- Large or empty input data.
- Duplicates and constraint violations.
- Extreme date/time values.
- Concurrent or conflicting requests.

**Example Test:**
```python
def test_document_with_very_large_content(self):
    """Test handling of documents with very large content."""
    self.client.force_authenticate(user=self.user)
    large_content = 'A' * 1000000  # 1MB of text
    response = self.client.post('/api/document-management/documents/', {
        'title': 'Large Document',
        'content': large_content
    })
    self.assertEqual(response.status_code, 201)
    
def test_concurrent_document_update(self):
    """Test handling of concurrent updates to the same document."""
    doc = Document.objects.create(title="Concurrent Doc", created_by=self.user)
    
    # Simulate concurrent updates
    with transaction.atomic():
        doc1 = Document.objects.select_for_update().get(id=doc.id)
        doc1.title = "Updated by thread 1"
        
        # This should raise an exception due to row lock
        with self.assertRaises(OperationalError):
            with transaction.atomic():
                doc2 = Document.objects.select_for_update(nowait=True).get(id=doc.id)
                doc2.title = "Updated by thread 2"
                doc2.save()
        
        doc1.save()
```

---

## ⚡ Stage 9: Performance Testing

**Purpose:**  
Evaluate system responsiveness and scalability under load.

**What to cover:**
- API latency under simulated user load.
- ORM query optimization and DB indexing.
- Caching effectiveness.
- Throughput, memory usage, and CPU load.

**Example Test:**
```python
def test_document_list_query_performance(self):
    """Test that document listing is optimized with select_related and prefetch_related."""
    # Create test data
    category = DocumentCategory.objects.create(name="Test Category")
    for i in range(100):
        Document.objects.create(
            title=f"Document {i}",
            created_by=self.user,
            category=category
        )
    
    # Count queries
    with self.assertNumQueries(3):  # Should be optimized to 3 queries
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/document-management/documents/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 100)
```

---

## 🛡️ Stage 10: Security Testing

**Purpose:**  
Protect the system against common web vulnerabilities and ensure safe data handling.

**What to cover:**
- SQL injection and XSS input sanitization.
- CSRF protection on forms and APIs.
- Secure password storage (hashing, salting).
- Authorization bypass attempts.
- Proper handling of sensitive data.

**Example Test:**
```python
def test_sql_injection_prevention(self):
    """Test that SQL injection attempts are prevented."""
    self.client.force_authenticate(user=self.user)
    injection_attempt = "'; DROP TABLE documents; --"
    response = self.client.get(f'/api/document-management/documents/?search={injection_attempt}')
    self.assertEqual(response.status_code, 200)
    # Verify that no tables were dropped
    self.assertTrue(Document.objects.exists())
    
def test_xss_prevention(self):
    """Test that XSS attempts are sanitized."""
    self.client.force_authenticate(user=self.user)
    xss_content = "<script>alert('XSS')</script>"
    response = self.client.post('/api/document-management/documents/', {
        'title': 'XSS Test',
        'content': xss_content
    })
    self.assertEqual(response.status_code, 201)
    doc = Document.objects.get(id=response.data['id'])
    # Content should be escaped or sanitized
    self.assertNotEqual(doc.content, xss_content)
```

---

## 🧼 Stage 11: Regression Testing

**Purpose:**  
Ensure that previously working functionality continues to work after updates or refactors.

**What to cover:**
- Key user workflows re-tested after changes.
- Bug reproduction tests added to test suite.
- Maintain test coverage for critical paths.

**Example Test:**
```python
def test_bug_123_document_status_not_updating(self):
    """Regression test for bug #123 where document status wasn't updating."""
    doc = Document.objects.create(title="Test Doc", created_by=self.user, status="draft")
    doc.status = "published"
    doc.save()
    doc.refresh_from_db()
    self.assertEqual(doc.status, "published")  # Verify fix works
```

---

## 🔁 Stage 12: CI/CD Integration & Automation

**Purpose:**  
Automate test execution and integrate into deployment pipelines.

**What to do:**
- Run test suites on push/PR using GitHub Actions, GitLab CI, etc.
- Prevent deployments if tests fail.
- Use coverage reports to track test completeness.
- Optionally deploy and test in staging environments.

**Example GitHub Actions Workflow:**
```yaml
name: Django Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:12
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
          
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
        
    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run Tests
      run: |
        coverage run --source='.' manage.py test
        coverage report
        
    - name: Upload Coverage Report
      uses: codecov/codecov-action@v1
```

---

## 📁 Suggested Test Structure

```
tests/
├── document_management/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_documents.py
│   │   ├── test_categories.py
│   │   ├── test_templates.py
│   │   ├── test_collections.py
│   │   ├── test_relationships.py
│   │   ├── test_metadata.py
│   │   ├── test_comments.py
│   │   ├── test_approvals.py
│   │   ├── test_signature_requests.py
│   │   └── factories.py  # optional: test data generators
│
├── applications/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_applications.py
│   │   └── test_transitions.py
│
├── borrowers/
│   ├── tests/
│   │   └── test_borrowers.py
│
├── brokers/
│   ├── tests/
│   │   └── test_brokers.py
│
├── calculator/
│   ├── tests/
│   │   ├── test_calculations.py
│   │   ├── test_repayments.py
│   │   └── test_fees.py
│
├── notifications/
│   ├── tests/
│   │   ├── test_notifications.py
│   │   └── test_notes.py
│
├── products/
│   ├── tests/
│   │   └── test_products.py
---

## ✅ Best Practices

- Use `setUpTestData()` for shared test setup across methods.
- Run tests with `coverage run manage.py test` and check results.
- Isolate test DB (e.g., in-memory SQLite) to speed up test runs.
- Use factories or fixtures to avoid manual object creation.
- Keep tests atomic and idempotent.
- Name tests descriptively to serve as documentation.
- Test both positive and negative scenarios.
- Mock external services to avoid network dependencies.
- Use parameterized tests for similar test cases with different inputs.
- Maintain at least 80% code coverage for critical paths.

---

