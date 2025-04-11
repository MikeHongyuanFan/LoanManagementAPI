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

## Document Collections

Document collections allow users to organize documents into folders or collections, similar to a file system.

### Key Features

- **Hierarchical Structure**: Collections can have subcollections, creating a folder-like hierarchy
- **Sharing**: Collections can be shared with specific users
- **Visual Customization**: Collections can have custom icons and colors
- **Document Count**: Automatic tracking of document count in collections and subcollections

### Usage Examples

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

## Document Relationships

Document relationships allow establishing connections between related documents, creating a network of related information.

### Relationship Types

- **Supersedes**: Document replaces another document
- **Supplements**: Document provides additional information
- **References**: Document refers to another document
- **Requires**: Document requires another document
- **Amends**: Document amends another document
- **Custom**: User-defined relationship type

### Usage Examples

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

## Custom Metadata Fields

Custom metadata fields allow adding flexible metadata to documents beyond the standard fields.

### Field Types

- **Text**: Single-line or multi-line text
- **Number**: Numeric values
- **Date**: Date values
- **Boolean**: True/false values
- **Select**: Selection from predefined options

### Usage Examples

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

## Enhanced Document Categorization

Enhanced document categorization provides a more flexible way to categorize documents.

### Key Features

- **Hierarchical Categories**: Categories can have subcategories
- **Auto-categorization Rules**: Rules for automatically categorizing documents
- **Visual Customization**: Categories can have custom icons and colors

### Usage Examples

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

## Document Organization Actions

Additional actions for organizing documents.

### Key Features

- **Favorite Documents**: Mark documents as favorites for quick access
- **Pin Documents**: Pin important documents to the top
- **Multiple Collections**: Add documents to multiple collections

### Usage Examples

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

## Implementation Details

### Database Models

- **DocumentCollection**: For organizing documents into collections
- **DocumentRelationship**: For defining relationships between documents
- **CustomMetadataField**: For defining custom metadata fields
- **DocumentMetadata**: For storing custom metadata values
- **Enhanced DocumentCategory**: With additional fields for hierarchical structure and visual customization
- **Enhanced Document**: With additional fields for organization features

### API Endpoints

- Collection management endpoints
- Relationship management endpoints
- Custom metadata management endpoints
- Document organization action endpoints

## Benefits

1. **Improved Organization**: Better ways to organize and find documents
2. **Enhanced Collaboration**: Sharing collections for team collaboration
3. **Flexible Metadata**: Custom metadata for different document types
4. **Document Connections**: Establish relationships between related documents
5. **Visual Organization**: Visual cues with icons and colors
6. **Quick Access**: Favorites and pinned documents for quick access
