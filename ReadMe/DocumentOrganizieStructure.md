# Advanced Document Organization Features

This document outlines the advanced document organization features implemented in the CRM Loan Management System.

## Features Overview

1. **Document Collections/Folders**
   - Hierarchical folder structure for organizing documents
   - Sharing capabilities for collaboration
   - Nested collections with parent-child relationships
   - Visual customization with icons and colors

2. **Document Relationships**
   - Define relationships between documents (supersedes, supplements, references, etc.)
   - Custom relationship types for flexibility
   - Bidirectional relationship tracking

3. **Custom Metadata Fields**
   - Define custom metadata fields for different document types
   - Multiple field types (text, number, date, boolean, select)
   - Document type-specific metadata fields

4. **Enhanced Document Categorization**
   - Hierarchical categories with parent-child relationships
   - Auto-categorization rules
   - Visual customization with icons and colors

5. **Document Organization Actions**
   - Favorite documents for quick access
   - Pin important documents
   - Add documents to multiple collections

## API Reference

### Document Collections

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/collections/` | GET | List all collections |
| `/api/document-management/collections/` | POST | Create a new collection |
| `/api/document-management/collections/{id}/` | GET | Get collection details |
| `/api/document-management/collections/{id}/` | PUT | Update a collection |
| `/api/document-management/collections/{id}/` | PATCH | Partially update a collection |
| `/api/document-management/collections/{id}/` | DELETE | Delete a collection |
| `/api/document-management/collections/{id}/subcollections/` | GET | Get all subcollections of a collection |
| `/api/document-management/collections/{id}/documents/` | GET | Get all documents in a collection |
| `/api/document-management/collections/{id}/share/` | POST | Share a collection with users |
| `/api/document-management/collections/{id}/unshare/` | POST | Unshare a collection with users |
| `/api/document-management/documents/{id}/add_to_collection/` | POST | Add document to collection |
| `/api/document-management/documents/{id}/remove_from_collection/` | POST | Remove document from collection |

### Document Relationships

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/relationships/` | GET | List all relationships |
| `/api/document-management/relationships/` | POST | Create a new relationship |
| `/api/document-management/relationships/{id}/` | GET | Get relationship details |
| `/api/document-management/relationships/{id}/` | PUT | Update a relationship |
| `/api/document-management/relationships/{id}/` | PATCH | Partially update a relationship |
| `/api/document-management/relationships/{id}/` | DELETE | Delete a relationship |
| `/api/document-management/documents/{id}/add_relationship/` | POST | Add a relationship to another document |
| `/api/document-management/documents/{id}/relationships/` | GET | Get all relationships for a document |

### Custom Metadata

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/metadata-fields/` | GET | List all metadata fields |
| `/api/document-management/metadata-fields/` | POST | Create a new metadata field |
| `/api/document-management/metadata-fields/{id}/` | GET | Get metadata field details |
| `/api/document-management/metadata-fields/{id}/` | PUT | Update a metadata field |
| `/api/document-management/metadata-fields/{id}/` | PATCH | Partially update a metadata field |
| `/api/document-management/metadata-fields/{id}/` | DELETE | Delete a metadata field |
| `/api/document-management/metadata-fields/for_document_type/` | GET | Get metadata fields for a specific document type |
| `/api/document-management/metadata/` | GET | List all metadata values |
| `/api/document-management/metadata/` | POST | Create a new metadata value |
| `/api/document-management/metadata/{id}/` | GET | Get metadata value details |
| `/api/document-management/metadata/{id}/` | PUT | Update a metadata value |
| `/api/document-management/metadata/{id}/` | PATCH | Partially update a metadata value |
| `/api/document-management/metadata/{id}/` | DELETE | Delete a metadata value |
| `/api/document-management/documents/{id}/add_metadata/` | POST | Add custom metadata to a document |

### Document Categories

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/categories/` | GET | List all categories |
| `/api/document-management/categories/` | POST | Create a new category |
| `/api/document-management/categories/{id}/` | GET | Get category details |
| `/api/document-management/categories/{id}/` | PUT | Update a category |
| `/api/document-management/categories/{id}/` | PATCH | Partially update a category |
| `/api/document-management/categories/{id}/` | DELETE | Delete a category |
| `/api/document-management/categories/{id}/subcategories/` | GET | Get all subcategories of a category |

### Document Organization Actions

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/documents/{id}/toggle_favorite/` | POST | Toggle favorite status |
| `/api/document-management/documents/{id}/toggle_pinned/` | POST | Toggle pinned status |

## Usage Examples

### Document Collections

Document collections allow users to organize documents into folders or collections, similar to a file system.

#### Creating a Collection

```
POST /api/document-management/collections/
```

Request:
```json
{
  "name": "Loan Applications",
  "description": "All loan application documents",
  "parent": null,
  "icon": "fa-folder",
  "color": "#4287f5"
}
```

#### Adding a Document to a Collection

```
POST /api/document-management/documents/1/add_to_collection/
```

Request:
```json
{
  "collection_id": 1
}
```

#### Sharing a Collection

```
POST /api/document-management/collections/1/share/
```

Request:
```json
{
  "user_ids": [2, 3, 4]
}
```

### Document Relationships

Document relationships allow establishing connections between related documents, creating a network of related information.

#### Relationship Types

- **Supersedes**: Document replaces another document
- **Supplements**: Document provides additional information
- **References**: Document refers to another document
- **Requires**: Document requires another document
- **Amends**: Document amends another document
- **Custom**: User-defined relationship type

#### Creating a Relationship

```
POST /api/document-management/relationships/
```

Request:
```json
{
  "source_document": 1,
  "target_document": 2,
  "relationship_type": "supersedes",
  "description": "This agreement supersedes the previous version"
}
```

#### Creating a Custom Relationship

```
POST /api/document-management/relationships/
```

Request:
```json
{
  "source_document": 1,
  "target_document": 3,
  "relationship_type": "custom",
  "custom_type": "depends_on",
  "description": "This document depends on the referenced document"
}
```

### Custom Metadata Fields

Custom metadata fields allow adding flexible metadata to documents beyond the standard fields.

#### Field Types

- **Text**: Single-line or multi-line text
- **Number**: Numeric values
- **Date**: Date values
- **Boolean**: True/false values
- **Select**: Selection from predefined options

#### Creating a Metadata Field

```
POST /api/document-management/metadata-fields/
```

Request:
```json
{
  "name": "Property Address",
  "description": "Address of the property",
  "field_type": "text",
  "required": true,
  "document_types": ["property", "agreement"]
}
```

#### Creating a Select Field

```
POST /api/document-management/metadata-fields/
```

Request:
```json
{
  "name": "Document Status",
  "description": "Custom status for document",
  "field_type": "select",
  "required": false,
  "default_value": "pending",
  "options": ["pending", "in_review", "final", "archived"]
}
```

#### Adding Metadata to a Document

```
POST /api/document-management/documents/1/add_metadata/
```

Request:
```json
{
  "field_id": 1,
  "value": "123 Main St, Anytown, CA 12345"
}
```

### Enhanced Document Categorization

Enhanced document categorization provides a more flexible way to categorize documents.

#### Creating a Category

```
POST /api/document-management/categories/
```

Request:
```json
{
  "name": "Financial Documents",
  "description": "All financial documents",
  "parent": null,
  "icon": "fa-file-invoice-dollar",
  "color": "#42f587",
  "auto_categorize_rules": {
    "keywords": ["financial", "statement", "balance", "income"],
    "document_types": ["financial"]
  }
}
```

### Document Organization Actions

Additional actions for organizing documents.

#### Toggle Favorite Status

```
POST /api/document-management/documents/1/toggle_favorite/
```

Response:
```json
{
  "is_favorite": true
}
```

#### Toggle Pinned Status

```
POST /api/document-management/documents/1/toggle_pinned/
```

Response:
```json
{
  "is_pinned": true
}
```

## Filter Parameters

The document management API endpoints support filtering, searching, and ordering:

- **Filter fields**: `document_type`, `category`, `status`, `application`, `is_confidential`, `is_favorite`, `is_pinned`
- **Search fields**: `title`, `description`, `keywords`
- **Ordering fields**: `title`, `created_at`, `updated_at`, `status`

Example:
```
GET /api/document-management/documents/?document_type=agreement&is_favorite=true&ordering=-created_at
```

## Implementation Details

### Database Models

- **DocumentCollection**: For organizing documents into collections
- **DocumentRelationship**: For defining relationships between documents
- **CustomMetadataField**: For defining custom metadata fields
- **DocumentMetadata**: For storing custom metadata values
- **Enhanced DocumentCategory**: With additional fields for hierarchical structure and visual customization
- **Enhanced Document**: With additional fields for organization features

## Benefits

1. **Improved Organization**: Better ways to organize and find documents
2. **Enhanced Collaboration**: Sharing collections for team collaboration
3. **Flexible Metadata**: Custom metadata for different document types
4. **Document Connections**: Establish relationships between related documents
5. **Visual Organization**: Visual cues with icons and colors
6. **Quick Access**: Favorites and pinned documents for quick access
