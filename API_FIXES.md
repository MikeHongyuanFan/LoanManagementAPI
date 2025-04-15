# API Implementation Fixes

## Overview

After investigating the API implementations and test failures, I've identified several issues that need to be fixed to make the tests pass. This document outlines the problems and proposed solutions.

## 1. Document Approval API

### Issues:
- The test is sending `document` in the request body, but the API expects `document_id` to be in the URL
- The test is sending `reviewer` in the request body, but the API expects `reviewer_id`
- The test is using `documentapproval-approve` endpoint, but the correct endpoint is `respond-to-approval`

### Solutions:
- Update the test to use the correct URL parameter `document_id` instead of including document in the request body
- Update the test to use `reviewer_id` instead of `reviewer` in the request body
- Update the test to use the correct endpoint `respond-to-approval` with the correct parameters

## 2. Document Signature API

### Issues:
- The test is sending `signer` in the request body, but the API expects `signer_id`
- The test is sending `action: 'sign'` in the request body, but the API expects `status: 'signed'`

### Solutions:
- Update the test to use `signer_id` instead of `signer` in the request body
- Update the test to use `status: 'signed'` instead of `action: 'sign'` in the request body

## 3. Calculator API

### Issues:
- The API is not correctly associating fees with calculations
- The API is not returning the calculation ID in the response
- The product association is not being properly set in the calculation

### Solutions:
- Fix the fee calculation logic in the calculator API
- Update the API to return the calculation ID in the response
- Ensure the product is properly associated with the calculation

## 4. Application Creation API

### Issues:
- The test is using the borrower user to create an application, but this might not have the required permissions
- The request format might not match what the API expects

### Solutions:
- Update the test to use the staff user to create the application
- Ensure the request format matches what the API expects

## Implementation Plan

1. Fix the document approval test:
   - Update the request body to use `reviewer_id` instead of `reviewer`
   - Update the endpoint to use `respond-to-approval` with the correct parameters

2. Fix the document signature test:
   - Update the request body to use `signer_id` instead of `signer`
   - Update the request body to use `status: 'signed'` instead of `action: 'sign'`

3. Fix the calculator API:
   - Update the API to correctly associate fees with calculations
   - Update the API to return the calculation ID in the response
   - Ensure the product is properly associated with the calculation

4. Fix the application creation test:
   - Update the test to use the staff user to create the application
   - Ensure the request format matches what the API expects

## Expected Results

After implementing these fixes, all tests should pass, and the API implementations should be consistent with the expected behavior.
