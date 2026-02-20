# **Extended Brief: `contacts.json` for Obsidian-Mac-Desktop-App (obsc-app) & uDOS**
**Focus:** Standardized contact management, data protection, and workflow integration

---

## **1. Overview**
The `contacts.json` system is designed to:
- **Centralize contact data** for both **personal** (`@user/contacts.json`) and **project-specific** (`@binders/[project]/contacts.json`) use.
- **Sync securely** between macOS (obsc-app) and uDOS (shell/cloud), ensuring **user data protection** and **project data isolation**.
- **Enhance workflows** by linking contacts to tasks (`moves.json`) and missions, while **parsing and summarizing emails** (without storing full email content).
- **Use symlinks/fallbacks** to merge personal and project contacts seamlessly.

---

## **2. File Structure & Location**

### **A. Personal Contacts**
- **Path:** `@user/contacts.json`
- **Scope:** User-wide contacts (e.g., personal, clients, collaborators).
- **Access:** Global (available to all projects via symlink/fallback).

### **B. Project/Binder Contacts**
- **Path:** `@binders/[project_name]/contacts.json`
- **Scope:** Project-specific contacts (e.g., stakeholders, team members, vendors).
- **Access:** Local to the project, but can reference `@user/contacts.json` via symlink/fallback.

---

## **3. `contacts.json` Schema**

### **Core Fields**
| Field               | Type          | Description                                                                                     | Example                                  |
|---------------------|---------------|-------------------------------------------------------------------------------------------------|------------------------------------------|
| `contact_id`        | String (UUID) | Unique identifier for the contact.                                                              | `"ct_abc123"`                            |
| `name`              | String        | Full name of the contact.                                                                       | `"Jane Doe"`                             |
| `email`             | Array         | List of email addresses.                                                                        | `["jane@company.com", "jane.doe@personal.com"]` |
| `phone`             | Array         | List of phone numbers.                                                                          | `["+123456789", "+987654321"]`           |
| `organization`      | String        | Company/organization name.                                                                      | `"Acme Inc."`                            |
| `role`              | String        | Role/title of the contact.                                                                      | `"Project Manager"`                      |
| `linked_missions`   | Array         | Mission/binder IDs where this contact is involved.                                              | `["mission_x", "mission_y"]`            |
| `linked_tasks`      | Array         | Task IDs (`moves.json`) associated with this contact.                                           | `["task_1", "task_2"]`                  |
| `email_summaries`   | Array         | Summaries of parsed emails (not full content). Linked to tasks if converted.                     | `[{"summary": "...", "date": "YYYY-MM-DD", "task_id": "task_1"}]` |
| `last_updated`      | String        | Timestamp of last update.                                                                       | `"2026-02-20T10:00:00Z"`                |
| `source`            | String        | Source of the contact (e.g., "macOS", "uDOS", "manual").                                       | `"macOS"`                                |
| `tags`              | Array         | User-defined tags for categorization.                                                           | `["client", "vendor", "high-priority"]`  |

---

### **Example `contacts.json`**
```json
{
  "contacts": [
    {
      "contact_id": "ct_abc123",
      "name": "Jane Doe",
      "email": ["jane@company.com", "jane.doe@personal.com"],
      "phone": ["+123456789"],
      "organization": "Acme Inc.",
      "role": "Project Manager",
      "linked_missions": ["mission_x"],
      "linked_tasks": ["task_1"],
      "email_summaries": [
        {
          "summary": "Follow up on project timeline. Deadline: 2026-03-01.",
          "date": "2026-02-19",
          "task_id": "task_1"
        }
      ],
      "last_updated": "2026-02-20T10:00:00Z",
      "source": "macOS",
      "tags": ["client", "high-priority"]
    }
  ]
}
```

---

## **4. Data Protection & Sync Logic**

### **A. User Data vs. Project Data**
- **Personal contacts** (`@user/contacts.json`) are **never overwritten** by project syncs.
- **Project contacts** (`@binders/[project]/contacts.json`) are **isolated** and only merged with personal contacts via **symlink/fallback** for read-only access.
- **Emails** are **parsed and summarized**, but **never stored in full** in `contacts.json` or uDOS/obsc-app.

### **B. Sync Process**
1. **macOS (obsc-app) → uDOS:**
   - Contacts from macOS Contacts app are synced to `@user/contacts.json`.
   - Only **new or updated** contacts are pushed to uDOS.
   - **Project contacts** are synced to their respective `@binders/[project]/contacts.json`.

2. **uDOS → macOS (obsc-app):**
   - Personal contacts (`@user/contacts.json`) are pulled and merged with macOS Contacts.
   - Project contacts remain in their binders and are **not** synced to macOS Contacts.

3. **Email Handling:**
   - Incoming emails are **parsed** for contact info (e.g., sender, recipients).
   - **Summaries** (not full emails) are added to `email_summaries` in `contacts.json`.
   - If an email is **converted to a task** (`moves.json`), the `task_id` is linked in `email_summaries`.

---

## **5. Symlink/Fallback System**
- **Purpose:** Allow projects to access **both personal and project contacts** without duplicating data.
- **Implementation:**
  - Each `@binders/[project]/contacts.json` includes a **symlink/fallback** to `@user/contacts.json`.
  - When a contact is requested:
    1. Check `@binders/[project]/contacts.json`.
    2. If not found, **fall back** to `@user/contacts.json`.
  - **Read-only:** Projects cannot modify personal contacts.

---

## **6. Workflow Integration**

### **A. Email to Task Conversion**
1. **Parse Email:**
   - Extract sender/recipient info, subject, and key details.
   - Generate a **summary** (e.g., "Follow up on contract. Deadline: 2026-03-01.").
2. **Update `contacts.json`:**
   - Add summary to `email_summaries` for the relevant contact.
3. **Offer Task Conversion:**
   - Prompt user: *"Convert this email to a task?"*
   - If yes, create a task in `moves.json` and link it to the contact via `linked_tasks` and `task_id` in `email_summaries`.

### **B. Contact Linking in Tasks**
- Tasks in `moves.json` can reference contacts via `linked_contacts`:
  ```json
  {
    "task_id": "task_1",
    "title": "Follow up with Jane Doe",
    "linked_contacts": ["ct_abc123"],
    "status": "pending"
  }
  ```

### **C. Mission/Project Scoping**
- Contacts in `@binders/[project]/contacts.json` are **automatically linked** to the mission via `linked_missions`.
- Example:
  ```json
  "linked_missions": ["mission_x"]
  ```

---

## **7. Data Cleanup & Archiving**
- **Emails:**
  - After parsing, emails can be **archived or trashed** on the remote server (user option).
  - Only summaries are retained in `contacts.json`.
- **Contacts:**
  - Inactive contacts (no linked tasks/missions for >1 year) can be **archived** to `@user/contacts_archive.json` or `@binders/[project]/contacts_archive.json`.

---

## **8. Example Workflow**

### **Scenario: Incoming Email**
1. **Email Received:**
   - From: `jane@company.com`
   - Subject: "Project Timeline Update"
2. **obsc-app/uDOS Action:**
   - Parse email → Extract contact (`Jane Doe`) and summary.
   - Update `@user/contacts.json` (or project `contacts.json` if relevant):
     ```json
     "email_summaries": [
       {
         "summary": "Project timeline updated. New deadline: 2026-03-01.",
         "date": "2026-02-19",
         "task_id": null
       }
     ]
     ```
   - Prompt: *"Convert to task?"*
3. **User Converts to Task:**
   - Task created in `moves.json`:
     ```json
     {
       "task_id": "task_1",
       "title": "Review project timeline with Jane Doe",
       "linked_contacts": ["ct_abc123"],
       "due_date": "2026-03-01"
     }
     ```
   - Update `contacts.json`:
     ```json
     "email_summaries": [
       {
         "summary": "Project timeline updated...",
         "date": "2026-02-19",
         "task_id": "task_1"
       }
     ],
     "linked_tasks": ["task_1"]
     ```

---

## **9. Implementation Notes**
- **Symlink Setup:**
  - Use OS-level symlinks or a custom JSON merge script to handle fallbacks.
- **Conflict Resolution:**
  - Prefer **user data** (`@user/contacts.json`) in conflicts.
- **Privacy:**
  - Never sync personal contacts to project folders without explicit user action.

---

## **10. Implementation Status (uDOS v1.4.4)**

### **Completed**
- [x] `.compost` archival directory with automatic versioning (2026-02-21)
- [x] Formatting service for Markdown to Marp slide conversion (2026-02-21)
- [x] Table extraction and JSON conversion (2026-02-21)
- [x] Vibe skill integration for document processing (2026-02-21)
- [x] Unified v1.4 specification document created (2026-02-21)
- [x] Wiki documentation for Vibe skill set (2026-02-21)

### **In Progress**
- [ ] Complete `contacts.json` schema implementation
- [ ] Complete `moves.json` schema implementation
- [ ] Build sync scripts for macOS ↔ uDOS
- [ ] Email parsing and task conversion Vibe skill
- [ ] Symlink/fallback merge logic for contact views

### **Next Steps**
- **Develop sync scripts** for macOS ↔ uDOS contact synchronization.
- **Create templates** for `contacts.json` and email summaries.
- **Test symlink/fallback** logic for performance and reliability.
- **User documentation** for email-to-task workflows and contact management.
- **Migration guide** from legacy task formats to v1.4 schema.
