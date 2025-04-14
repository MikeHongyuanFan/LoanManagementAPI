# Testing Workspace

This directory contains the testing structure for the Loan Application Backend project, organized by testing stages.

## Directory Structure

The testing workspace is organized into 12 stages, each focusing on a specific aspect of testing:

1. **Stage1_FunctionalTesting**: Verify that each individual API endpoint or view functions as intended under normal conditions.
2. **Stage2_InputValidation**: Ensure that the system handles bad or malformed input safely and consistently.
3. **Stage3_Authentication**: Confirm that only properly authenticated and authorized users can access protected routes.
4. **Stage4_ModelLogic**: Verify that model-level logic and relationships work correctly.
5. **Stage5_SerializerTesting**: Validate data transformation and validation using Django REST Framework serializers.
6. **Stage6_URLRouting**: Ensure that all URL patterns route to the correct views or viewsets.
7. **Stage7_IntegrationTesting**: Test the interaction between multiple components in complete flows.
8. **Stage8_EdgeCaseTesting**: Push the system to its edge cases to catch uncommon but critical issues.
9. **Stage9_PerformanceTesting**: Evaluate system responsiveness and scalability under load.
10. **Stage10_SecurityTesting**: Protect the system against common web vulnerabilities and ensure safe data handling.
11. **Stage11_RegressionTesting**: Ensure that previously working functionality continues to work after updates.
12. **Stage12_CICDIntegration**: Automate test execution and integrate into deployment pipelines.

Within each stage, tests are organized by application module:
- document_management
- applications
- borrowers
- brokers
- calculator
- notifications
- products

## Running Tests

To run tests for a specific stage:

```bash
# Run all tests in a stage
python manage.py test Testing.Stage1_FunctionalTesting

# Run tests for a specific module in a stage
python manage.py test Testing.Stage1_FunctionalTesting.document_management
```

To run all tests:

```bash
python manage.py test Testing
```

## Test Coverage

To generate a test coverage report:

```bash
coverage run --source='.' manage.py test Testing
coverage report
coverage html  # Generates HTML report in htmlcov/
```

## CI/CD Integration

The Stage12_CICDIntegration directory contains configuration files for integrating tests into CI/CD pipelines:

- GitHub Workflows
- Coverage Reports
- Deployment Scripts

## Adding New Tests

When adding new tests:

1. Place the test in the appropriate stage directory
2. Follow the naming convention: `test_*.py`
3. Ensure tests are independent and can run in isolation
4. Add appropriate documentation and comments

## Test Data

Test data factories are available in each module's `factories.py` file to help generate test data consistently.
