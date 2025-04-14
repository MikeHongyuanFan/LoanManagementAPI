
---

## 🧭 Centralized Dashboard API Structure: Concept Overview

A centralized dashboard UI should be **modular**, reflecting the **core domains** of the system, with each module clearly mapped to its associated API group. This structure ensures clean separation of concerns, logical navigation, and scalability.

---

## 🧱 Recommended Dashboard Architecture
### 0.1: Search/list based interactive function:
-- User is able to licking the list button to show all the application services, Or users are able to search application by input key words.
### 🔹 1. **Dashboard Layout Structure**

```
- Dashboard (Main Shell)
List/search bar input
  ├── 📁 Document Center
  │   ├── Documents
  │   ├── Categories
  │   ├── Templates
  │   ├── Collections
  │   ├── Metadata
  │   ├── Relationships
  │   ├── Comments
  │   ├── Approvals
  │   └── E-Signatures
  ├── 📁 Loan Management
  │   ├── Applications
  │   ├── Repayments
  │   ├── Loan Extensions
  ├── 📁 Entities
  │   ├── Borrowers
  │   ├── Brokers
  │   ├── Valuers
  │   └── Quantity Surveyors (QS)
  ├── 📁 Product Configuration
  │   ├── Products
  │   ├── Fees
  │   ├── Calculator (Fee, Repayment, Application Fees)
  ├── 📁 Notifications & Notes
  │   ├── Notifications
  │   └── Notes
  ├── ⚙️ System Settings (optional future module)
```

---

## 🔄 API Mapping by Dashboard Section

### 📁 Document Center

> Unified document management workflows

| Dashboard Feature     | API Groups |
|-----------------------|------------|
| Document Explorer     | Documents, Collections |
| Organization          | Categories, Metadata, Relationships |
| Collaboration         | Comments, Approvals, Signature Requests |
| Document Utilities    | Toggle Favorite, Pin, Add to Collection, Metadata, Relationships |

---

### 📁 Loan Management

> Core of CRM functionality

| Dashboard Feature         | API Groups |
|---------------------------|------------|
| Application Manager       | Applications (incl. transition/duplicate) |
| Repayment Tracker         | Repayments |
| Loan Extension Workflow   | Loan Extensions |

---

### 📁 Entities

> All actors involved in the loan process

| Dashboard Feature | API Groups |
|-------------------|------------|
| Borrower Manager  | Borrowers |
| Broker Manager    | Brokers |
| Valuers & QS      | Valuers, Quantity Surveyors |

---

### 📁 Product Configuration

> Loan rules and financial calculation logic

| Dashboard Feature         | API Groups |
|---------------------------|------------|
| Product Catalog           | Products |
| Fee Configuration         | Fees, Calculator Fees, Application Fees |
| Loan Calculator           | Calculations, Repayments, Calculate Endpoint |

---

### 📁 Notifications & Notes

> User communication and reminders

| Dashboard Feature     | API Groups |
|-----------------------|------------|
| Notification Center   | Notifications (includes unread, filtered) |
| Notes & Reminders     | Notes (with reminder support) |

---

## 🧠 Relationships & Data Flows

To maintain traceability and context:

- **Applications** link to → **Borrowers**, **Brokers**, **Products**, **Documents**, **Notes**, **Notifications**
- **Documents** can belong to → **Collections**, **Applications**, **Categories**
- **Documents** may be approved, commented on, or signed → approval/signature APIs
- **Calculator** is linked to **Products**, **Applications**, and **Fees**
- **Metadata** and **Relationships** act as enrichment layers over documents

---

## 📊 Optional Enhancements

- **Global Search Bar**: Search across borrowers, documents, applications.
- **Activity Timeline Widget**: Aggregate events from notifications, approvals, comments, and notes.
- **Contextual Side Panels**: Show borrower details when viewing an application, or linked documents when editing a product.

---

