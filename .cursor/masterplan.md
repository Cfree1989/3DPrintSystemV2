# 3D Print System Project Plan

## 1. Project Overview
This project will build a Flask-based 3D print job management system for an academic/makerspace setting that will run on two different computers. The system will handle the workflow from student submission to completion, with file tracking, staff approval, and the ability to open the exact uploaded files directly in local applications.

The project aims to replace potentially ad-hoc or manual 3D print request systems with a **centralized, digitally managed, and workflow-driven platform.** It prioritizes clarity, efficiency, and accurate file tracking, especially addressing the complexities of file changes introduced by slicer software, ultimately improving the experience for both students requesting prints and the staff managing the printing service.

## 2. Core Features & Requirements

### 2.1 Core Features
1.  **Student submission process**: Allow students to upload 3D model files (.stl, .obj, .3mf) with metadata (name, email, print parameters).
2.  **Staff approval workflow**: Enable staff to review, slice files, and approve/reject jobs.
3.  **Multi-computer support**: System works across two computers with consistent file access (via a single server instance, see Section 4.1.2).
4.  **File lifecycle management**: Track original files without creating duplicates; manage authoritative files post-slicing.
5.  **Job status tracking**: Clear progression through Uploaded → Pending → ReadyToPrint → Printing → Completed → PaidPickedUp, and Rejected.
6.  **Email notifications**: Automated updates to students at key job stages (approval, rejection, completion, confirmation requests).
7.  **Thumbnails**: Generate previews from uploaded files for easy identification (e.g., using a library like Trimesh). If thumbnail generation fails, no thumbnail will be displayed, or a generic placeholder may be shown if simple to implement.

### 2.2 Technical Requirements
-   **Backend**: Flask with SQLAlchemy (SQLite initially).
-   **Frontend**: Tailwind CSS and Alpine.js for light interactivity. Development will prioritize semantic HTML for basic accessibility. Advanced accessibility features or audits are out of scope for the initial version.
-   **Authentication**: Simple staff-wide shared password.
-   **File handling**: Shared network storage accessible to both computers.
-   **Direct file opening**: Custom protocol handler to open local files in slicer software.
-   **Email**: Flask-Mail for notifications.
-   **Database**: SQLite with Flask-Migrate for schema management.
-   **Critical Dependencies**: Flask-WTF for form handling and CSRF protection (essential for SubmissionForm functionality and security). Also required: WTForms with EmailValidator, DataRequired, Length validators.

### 2.3 Simplified Architecture Principles
This project will adhere to simplicity:
1.  **Authentication**: Single shared staff password for dashboard access.
2.  **Models**: Essential `Job` model with student info and file metadata.
3.  **File Management**: Straightforward folder structure based on job status, accessible via shared network.
4.  **Routes**: Core functionality for submission, approval, and status updates.
5.  **Testing**: Focus on basic functionality and file handling.

### 2.4 User Experience Requirements
Based on operational needs, the following UX features are critical:
-   **Dynamic Form Behavior**: Color selection must be disabled until print method is selected, with contextual help text
-   **Progressive Disclosure**: Print method descriptions should be clearly visible to guide material choice
-   **Input Validation**: Real-time client-side validation with visual feedback to prevent submission errors
-   **Educational Content**: Comprehensive introduction text with liability disclaimers and scaling guidance
-   **Accessibility**: Visual error states with red borders, clear error messages, and error scrolling for form submission
-   **File Validation**: Immediate feedback on file selection with size and type checking
-   **File handling**: Shared network storage accessible to both computers.
-   **Direct file opening**: Custom protocol handler to open local files in slicer software.
-   **Email**: Flask-Mail for notifications. SMTP credentials will be securely managed (e.g., via an .env file and application configuration). Advanced deliverability configurations (like SPF/DKIM records) are operational tasks external to the application and out of scope for initial development.
-   **Database**: SQLite with Flask-Migrate for schema management.

## 3. System Design & Structure

### 3.1 Project Structure
```
3DPrintSystem/
├── app/
│   ├── __init__.py             # App factory, setup database and extensions
│   ├── config.py               # Configuration (dev, test, prod environments)
│   ├── extensions.py           # Initialize extensions (SQLAlchemy, Mail, etc.)
│   ├── models/
│   │   ├── __init__.py
│   │   └── job.py              # Job model with status enum
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py             # Public routes (submit, confirm)
│   │   └── dashboard.py        # Staff routes (dashboard, job actions)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_service.py     # File handling, movement between status dirs
│   │   ├── email_service.py    # Email notifications
│   │   ├── cost_service.py     # Cost calculations
│   │   └── thumbnail_service.py # Generate thumbnails from 3D files (e.g., using Trimesh; gracefully handles failures by showing no thumbnail or a placeholder).
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── tokens.py           # Secure token generation for confirmation
│   │   ├── validators.py       # Form and file validation
│   │   └── helpers.py          # General utility functions
│   ├── static/
│   │   ├── css/
│   │   │   ├── tailwind.css    # Source file
│   │   │   └── build.css       # Compiled output
│   │   ├── js/
│   │   │   └── alpine.min.js   # Alpine.js (local copy or CDN)
│   │   └── img/
│   │       └── logo.png        # Site logo
│   └── templates/
│       ├── base.html           # Base template with common structure
│       ├── components/         # Reusable template components
│       │   ├── job_row.html    # Job list item template
│       │   ├── modal.html      # Reusable modal component
│       │   └── flash.html      # Flash message component
│       ├── main/               # Public pages
│       │   ├── index.html      # Homepage
│       │   ├── submit.html     # Upload form
│       │   ├── success.html    # Submission success
│       │   └── confirm.html    # Job confirmation page
│       ├── dashboard/          # Staff pages
│       │   ├── login.html      # Staff login
│       │   ├── index.html      # Main dashboard
│       │   └── job_detail.html # Job details modal
│       └── email/              # Email templates
│           ├── approved.html   # Job approved email
│           ├── rejected.html   # Job rejected email
│           └── completed.html  # Job completed email
├── migrations/                 # Database migrations (Flask-Migrate)
├── instance/                   # Instance-specific config (e.g., app.db)
├── storage/                    # File storage (outside app directory)
│   ├── Uploaded/
│   ├── Pending/
│   ├── ReadyToPrint/
│   ├── Printing/
│   ├── Completed/
│   ├── PaidPickedUp/
│   └── thumbnails/
├── tests/                      # Test suite
├── tools/                      # Support tools (e.g., SlicerOpener.py)
├── app.py                      # Entry point
└── various config files        # .env, requirements.txt, package.json, etc.
```

### 3.2 Data Model
```python
class Job(db.Model):
    id = db.Column(db.String, primary_key=True)   # uuid4 hex
    student_name = db.Column(db.String(100))
    student_email = db.Column(db.String(100))
    original_filename = db.Column(db.String(256)) # Original name from student upload
    display_name = db.Column(db.String(256))      # Standardized name (e.g., FirstLast_Method_Color_ID.ext) or slicer output name
    file_path = db.Column(db.String(512))         # Full network path to the authoritative file for the current status
    status = db.Column(db.String(50))             # Enum: UPLOADED, PENDING, REJECTED, READYTOPRINT, PRINTING, COMPLETED, PAIDPICKEDUP
    printer = db.Column(db.String(64))            # Selected printer type/method
    color = db.Column(db.String(32))
    material = db.Column(db.String(32))           # Entered by staff
    weight_g = db.Column(db.Float)                # Entered by staff
    time_min = db.Column(db.Integer)              # Entered by staff
    cost_usd = db.Column(db.Numeric(6, 2))        # Calculated
    student_confirmed = db.Column(db.Boolean, default=False)
    student_confirmed_at = db.Column(db.DateTime, nullable=True)
    confirm_token = db.Column(db.String(128), nullable=True, unique=True) # For student confirmation link
    confirm_token_expires = db.Column(db.DateTime, nullable=True)
    reject_reasons = db.Column(db.JSON, nullable=True) # List of strings or structured reasons
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_updated_by = db.Column(db.String(50), nullable=True) # "student" or "staff". Will be set to a generic "staff" identifier on any staff-initiated modification.
```

### 3.3 Authentication Approach
-   **Staff Authentication**: Session-based login using a single, shared staff password defined in the application configuration. Access to dashboard and administrative functions is protected. This approach is chosen for maximum simplicity in a small, trusted staff environment and does not provide individual user accountability for actions.
-   **Student Confirmation**: Token-based mechanism using `itsdangerous` for generating secure, time-limited tokens embedded in email links for job confirmation. This does not require student accounts.

### 3.4 Comprehensive Job Lifecycle: Statuses, Backend Processes, and UI Workflows

**Note on Original File Preservation:** Throughout the job lifecycle, the original file uploaded by the student (and referenced by `job.original_filename`) will be preserved in its initial storage location (e.g., within the `storage/Uploaded/` directory). This file will not be moved or deleted when staff create a sliced version that becomes the authoritative `job.file_path` for printing. The original uploaded file will only be removed according to the Data Retention Policy (see Section 5.X), ensuring it remains available for historical reference or if re-slicing is needed.

This section details the progression of a job through the system, including file management and automated communications. The authoritative file for a job is the one most recently processed and relevant for its current status (e.g., original upload, or staff-sliced file). The "Open File" button always targets this authoritative file.

**Standardized File Naming Convention**:
Upon initial successful upload, files are renamed to: `FirstAndLastName_PrintMethod_Color_SimpleJobID.original_extension`
(e.g., `JaneDoe_Filament_Blue_123.stl`). The `SimpleJobID` is derived from the `Job.id`. This `display_name` is stored in the database. If staff later save a sliced version with a new name/extension, the `display_name` and `file_path` are updated to reflect the new authoritative file.

1.  **Uploaded**
    *   **Trigger**: Student successfully submits the print job form.
    *   **File Operations**:
        *   Original uploaded file is validated (type, size).
        *   File is renamed according to the standardized convention.
        *   Stored in `storage/Uploaded/JaneDoe_Filament_Blue_123.stl`.
        *   `job.file_path` points to this location. `job.original_filename` stores the student's initial filename. `job.display_name` stores the standardized name.
        *   Thumbnail generated and stored in `storage/thumbnails/`.
    *   **Key Actions**: System automatically processes submission.
    *   **Email Notification**: None typically, student sees a success page. (Optional: initial submission receipt email).

    #### Student Submission UI/UX (Corresponds to 'Uploaded' Status)

    **Page Flow**:
    `Public Access (/submit)` → `Upload Form Page` → `POST to /submit` → `File Validation & Job Creation` → `Success Page (/submit/success?job=<id>)` OR `Upload Form Page with Errors`

    1.  **Upload Form (`/submit`)**:
        *   **Form Introduction**: Comprehensive warning text at the top of the form stating:
            "Before submitting your model for 3D printing, please ensure you have thoroughly reviewed our Additive Manufacturing Moodle page, read all the guides, and checked the checklist. If necessary, revisit and fix your model before submission. Your model must be scaled and simplified appropriately, often requiring a second version specifically optimized for 3D printing. We will not print models that are broken, messy, or too large. Your model must follow the rules and constraints of the machine. We will not fix or scale your model as we do not know your specific needs or project requirements. We print exactly what you send us; if the scale is wrong or you are unsatisfied with the product, it is your responsibility. We will gladly print another model for you at an additional cost. We are only responsible for print failures due to issues under our control."
        *   **Fields**:
            *   Student Name (text input, required, 2-100 characters)
            *   Student Email (email input, required, validated format, max 100 characters)
            *   Discipline (dropdown options, required): Art, Architecture, Landscape Architecture, Interior Design, Engineering, Hobby/Personal, Other
            *   Class Number (text input, required, format example: "ARCH 4000", max 50 characters, allows "N/A")
            *   Print Method (dropdown: "Filament", "Resin", required) with contextual descriptions:
                - Resin: Description: Super high resolution and detail. Slow. Best For: Small items. Cost: More expensive.
                - Filament: Description: Good resolution, suitable for simpler models. Fast. Best For: Medium items. Cost: Least expensive.
            *   Color Preference (dynamic dropdown, disabled until Print Method selected, required):
                - Filament Colors (23 options): True Red, True Orange, Light Orange, True Yellow, Dark Yellow, Lime Green, Green, Forest Green, Blue, Electric Blue, Midnight Purple, Light Purple, Clear, True White, Gray, True Black, Brown, Copper, Bronze, True Silver, True Gold, Glow in the Dark, Color Changing
                - Resin Colors (4 options): Black, White, Gray, Clear
            *   Scaling Question: "Will your model fit on our printers? Please check the dimensions (W x D x H): Filament - Prusa MK4S: 9.84" × 8.3" × 8.6" (250 × 210 × 220 mm), Prusa XL: 14.17''×14.17''×14.17'' (360 × 360 × 360 mm), Raise3D Pro 2 Plus: 12" × 12" × 23.8" (305 × 305 × 605 mm). Resin - Formlabs Form 3: 5.7 × 5.7 × 7.3H inches (145 x 145 x 175 mm). Ensure your model's dimensions are within the specified limits for the printer you plan to use. If your model is too large, consider scaling it down or splitting it into parts. For more guidance, refer to the design guides on our Moodle page or ask for assistance in person. If exporting as .STL or .OBJ you MUST scale it down in millimeters BEFORE exporting. If you do not the scale will not work correctly." (required response)
            *   Minimum Charge Consent: "I understand there is a minimum $3.00 charge for all print jobs, and that the final cost may be higher based on material and time." (checkbox, required)
            *   File Upload (input type `file`, required, .stl/.obj/.3mf only, 50MB max size)
            *   Submit Button
        *   **Client-Side Validation**: 
            - Real-time file validation (type and size checking on selection)
            - Email format validation on blur
            - Color dropdown state management (disabled until method selected)
            - Visual error feedback with red borders and error messages
            - Form submission validation for all field types
            - Error scrolling to first error on submission attempt
            - Submit button loading state during submission
        *   **Server-Side Validation**: All client-side checks re-validated, plus custom FileSizeLimit validator and enhanced field validation with Length validators.

    2.  **Success Page (`/submit/success?job=<id>`)**:
        *   Displays a success message.
        *   Shows the Job ID for reference.
        *   Provides clear "next steps" messaging (e.g., "Your submission is now with staff for review. You will receive an email if it's rejected or approved, asking for your final confirmation before printing.").

2.  **Pending** (Awaiting Student Confirmation)
    *   **Trigger**: Staff reviews an "Uploaded" job, enters estimated weight/time, and clicks "Approve".
    *   **File Operations**:
        *   Staff may open the file from `storage/Uploaded/` in slicer software.
        *   If staff saves a sliced version (e.g., `JaneDoe_Filament_Blue_123.gcode` or `JaneDoe_Filament_Blue_123.3mf`), this new file becomes the authoritative file.
        *   The authoritative file (original or sliced) is moved from `storage/Uploaded/` to `storage/Pending/`.
        *   `job.file_path` is updated to the new location in `storage/Pending/`.
        *   If sliced, `job.display_name` is updated to the new filename.
    *   **Key Actions**:
        *   Staff enters print parameters (weight, material, time) which are used for cost calculation.
        *   System generates a secure, time-limited confirmation token (e.g., valid for 7 days). `job.confirm_token` and `job.confirm_token_expires` are set.
    *   **Email Notification**: Confirmation email sent to student including:
        *   Job details (filename, print method, estimated cost, estimated time).
        *   Secure link (using `job.confirm_token`) to a confirmation page.
        *   Clear explanation that the print will not proceed without their confirmation.
        *   Token expiration information.

    #### Staff Approval UI/UX (Corresponds to 'Pending' Status)
    When staff click "Approve" on an "Uploaded" job:

    1.  **Approval Confirmation Modal**:
        *   Title: "Confirm Approval for Job [Job ID]"
        *   Message: "Are you sure you want to approve this print job? This will send an email to [student_email] asking for their final confirmation."
        *   Required Input Fields:
            *   Estimated Weight (g)
            *   Estimated Print Time (min)
            *   Material selection
        *   Display: Calculated Estimated Cost (updates based on inputs).
        *   Buttons: "Cancel", "Yes, Approve and Email Student".

3.  **Rejected**
    *   **Trigger**: Staff reviews an "Uploaded" job and clicks "Reject".
    *   **File Operations**:
        *   The file typically remains in `storage/Uploaded/` or may be moved to an `storage/Archived_Rejected/` folder after a period. Original uploaded file is preserved.
    *   **Key Actions**: Staff selects rejection reasons and may add custom notes.
    *   **Email Notification**: Rejection email sent to student including:
        *   Job details.
        *   Specific reasons for rejection.

    #### Staff Rejection UI/UX (Corresponds to 'Rejected' Status)
    When staff click "Reject" on an "Uploaded" job:

    1.  **Rejection Confirmation Modal**:
        *   Title: "Confirm Rejection for Job [Job ID]"
        *   Message: "Are you sure you want to reject this print job? This will send an email to [student_email] with the rejection reasons."
        *   Input Fields:
            *   Checkbox group for common rejection reasons (e.g., "Non-manifold geometry", "Walls too thin", "Unprintable features", "File errors", "Other").
            *   Textarea for "Additional details or custom reason".
        *   Buttons: "Cancel", "Yes, Reject and Email Student".
        *   Example HTML for Rejection Dialog:
            ```html
            <!-- Reject Confirmation Modal (Simplified) -->
            <div x-show="showRejectModal" class="modal">
              <div class="modal-content">
                <h3>Confirm Rejection</h3>
                <p>This will send an email to the student (<span x-text="job.student_email"></span>) with the rejection reasons.</p>
                <div class="form-group">
                  <label>Rejection Reason(s):</label>
                  <div class="checkbox-group">
                    <label><input type="checkbox" name="reasons[]" value="non_manifold"> Non-manifold geometry</label>
                    </div>
                  <textarea name="custom_reason" placeholder="Additional details..."></textarea>
                </div>
                <button @click="showRejectModal = false">Cancel</button>
                <button @click="rejectJob()">Yes, Reject and Email Student</button>
              </div>
            </div>
            ```

    **Benefits of Modals**: Prevents accidental actions, ensures necessary data is input, confirms email will be sent.

4.  **ReadyToPrint**
    *   **Trigger**: Student clicks the confirmation link in the "Pending" email and confirms the job on the confirmation page.
    *   **File Operations**:
        *   The authoritative file is moved from `storage/Pending/` to `storage/ReadyToPrint/`.
        *   `job.file_path` is updated.
    *   **Key Actions**:
        *   System validates the confirmation token (not expired, valid signature).
        *   `job.student_confirmed` is set to `True`, `job.student_confirmed_at` is recorded. `job.confirm_token` may be cleared.
    *   **Email Notification**: (Optional) Email to student confirming their job is now in the queue. Email/alert to staff that a job is ready.

5.  **Printing**
    *   **Trigger**: Staff selects a "ReadyToPrint" job and clicks "Mark Printing".
    *   **File Operations**:
        *   The authoritative file is moved from `storage/ReadyToPrint/` to `storage/Printing/`.
        *   `job.file_path` is updated.
    *   **Key Actions**: Staff physically starts the print on the selected printer.
    *   **Email Notification**: None typically to student at this stage.

6.  **Completed**
    *   **Trigger**: Staff clicks "Mark Complete" for a job that was "Printing".
    *   **File Operations**:
        *   The authoritative file is moved from `storage/Printing/` to `storage/Completed/`.
        *   `job.file_path` is updated.
    *   **Key Actions**: Staff removes the print from the printer.
    *   **Email Notification**: Completion email sent to student:
        *   Notifying them their print is ready for pickup.
        *   Pickup location and hours.
        *   Final cost if different from estimate.
        *   Link to a feedback form (e.g., Microsoft Form).

7.  **PaidPickedUp**
    *   **Trigger**: Staff clicks "Mark Picked Up" for a "Completed" job.
    *   **File Operations**:
        *   The authoritative file is moved from `storage/Completed/` to `storage/PaidPickedUp/` (or a general archive).
        *   `job.file_path` is updated. This status helps in archiving and cleanup.
    *   **Key Actions**: Student collects and (if applicable) pays for the print.
    *   **Email Notification**: None typically.

    #### General Staff Dashboard and Job Interaction UI/UX

    1.  **Main Dashboard Layout (`/dashboard`)**:
        *   Header: Logo, "Staff Dashboard", Staff Logout button.
        *   Status Tabs (Alpine.js driven): "Uploaded", "Pending", "ReadyToPrint", "Printing", "Completed", "PaidPickedUp", "Rejected". Each tab lists jobs in that status.
        *   Job List: Table or card layout for jobs.

    2.  **Job Row Details (in Job List)**:
        *   Thumbnail image.
        *   Student Name & Email.
        *   Display Name of the current authoritative file.
        *   Submission Date & Time (simple format, e.g., MM/DD - HH:MM).
        *   Printer, Color, Material (if entered).
        *   Estimated/Actual Cost (if calculated/entered).
        *   Action Buttons (contextual to status):
            *   Common: "Open File" (uses custom protocol, always opens authoritative file).
            *   `Uploaded`: "Approve", "Reject".
            *   `Pending`: "View Details", "Resend Confirmation Email", "Manually Confirm".
            *   `ReadyToPrint`: "Mark Printing".
            *   `Printing`: "Mark Complete".
            *   `Completed`: "Mark Picked Up".
            *   Any status: "View Details/Edit", "Add Note".

    3.  **Job Detail View/Modal (accessed from Job Row)**:
        *   Larger thumbnail.
        *   All job metadata from `Job` model.
        *   **Editable fields for staff**: Material, Weight (g), Print Time (min), Printer (if needs changing), Color (if needs changing).
        *   Calculated Cost (updates if editable fields change).
        *   Full status history log for the job.
        *   Staff Notes field (internal comments).
        *   Administrative override controls (see next section).

    #### Administrative Controls & Manual Overrides UI/UX
    (Accessible typically from Job Detail View/Modal for authorized staff)

    1.  **Status Override Controls**:
        *   Dropdown to manually change job status to any valid state.
        *   Associated file movement happens automatically in the backend as per "Job Lifecycle".
        *   Option to manually mark a "Pending" job as confirmed.
        *   Option to reset confirmation for a "Pending" job (invalidates old token, can trigger new email).

    2.  **File Management Controls**:
        *   Option to upload a new version of a file, replacing the current authoritative file.
        *   Option to download the current authoritative file.
        *   (Potentially) Option to delete a job's file(s) if necessary (with warnings).

    3.  **Email Control During Overrides**:
        *   **Default**: Manual status changes via these admin controls DO NOT automatically trigger standard student emails.
        *   **Explicit Option**: A checkbox like "Send standard notification email to student for this change?" is provided.
        *   Logging: All manual overrides and decisions to send/suppress emails are logged.

    4.  **Other Administrative Actions**:
        *   Adding/editing internal staff notes on a job.
        *   (Future) Batch operations, job duplication.

**Fallback/Manual Processes for Pending Status:**
*   If a student doesn't confirm within the token expiry period, staff are alerted (e.g., via dashboard).
*   Staff can manually resend a confirmation email (generating a new token).
*   Staff can manually mark a job as confirmed if email confirmation fails (e.g., student confirms verbally). This action is logged.

## 4. Technical Deep Dive: Direct File Access

### 4.1 Multi-Computer Architecture
1.  **Shared File Storage**:
    *   All job-related files (uploads, sliced files, thumbnails) stored on a network share.
    *   Both computers must map this share to an identical path (e.g., `Z:\3DPrintFiles\` or via UNC path `\\SERVER\3DPrintFiles\`).
    *   The Flask application (running on one computer or both, see Database Options) will reference files using this shared path.
2.  **Database Options**:
    *   **Chosen Approach (Simplified SQLite Usage)**: The system will use SQLite as initially planned. To ensure data integrity and avoid concurrency issues, the Flask application (and thus direct database write access) will run on **a single, designated staff computer** acting as the server. 
    *   The SQLite database file (`app.db`) can reside on this server computer's local disk or on a network share, provided it is reliably accessible by this *single server instance*.
    *   Other staff members will access the application via their web browsers, connecting to the Flask application hosted on the designated server computer.
    *   This model eliminates the risks of concurrent writes to SQLite from multiple application instances, making it a robust simple solution. Option A (SQLite on a share with multiple app instances) is explicitly avoided due to high risk of corruption. Option B (dedicated database server like PostgreSQL/MySQL) is considered out of scope for the initial simplest system.

### 4.2 Custom Protocol Handler
*   A custom URL protocol (e.g., `3dprint://`) will be registered on both staff computers.
*   Example URL: `3dprint://open?path=Z:\storage\Uploaded\JaneDoe_Filament_Blue_123.stl`

### 4.3 File Opening Solution
1.  **Custom Protocol Registration (Windows Example)**:
    ```
    Windows Registry:
    HKEY_CLASSES_ROOT\3dprint\shell\open\command
    (Default) = "C:\Path\To\SlicerOpener.exe" "%1"
    ```
    (A `.bat` or `.reg` file can automate this setup on staff machines).
2.  **Helper Application (`SlicerOpener.py`)**:
    *   A small Python script (compiled to `.exe` using PyInstaller).
    *   Takes the `3dprint://` URL as an argument.
    *   Parses the file path from the URL.
    *   **Crucially, it must perform robust security validation:**
        *   The extracted file path must be normalized and converted to an absolute path.
        *   It must be verified to be strictly within the `AUTHORITATIVE_STORAGE_BASE_PATH` to prevent path traversal or access to unauthorized locations.
        *   The script should log all validation attempts and their outcomes.
    *   **User-Facing Error Handling:**
        *   The script must provide clear, user-friendly error messages (e.g., via simple GUI dialogs using a library like `tkinter.messagebox` if compiled) for issues such as:
            *   Invalid or missing file path in the URL.
            *   Security validation failure.
            *   File not found at the specified path.
            *   Slicer executable not found or failed to launch.
            *   Other exceptions during file opening.
    *   **Logging:**
        *   The script should perform local file logging for auditing and troubleshooting. Logs should include:
            *   Timestamp of the request.
            *   The full `3dprint://` URI received.
            *   Result of security validation.
            *   Success or failure of opening the file.
            *   Any errors encountered.
    *   Launches the appropriate slicer software, passing the validated file path to it.
    *   (Future enhancement: Could check file extension to open in different slicers).
    ```python
    # SlicerOpener.py (Conceptual)
    import sys, subprocess, os # Added os module
    from urllib.parse import urlparse, parse_qs
    # For GUI error messages (optional, example)
    # import tkinter
    # from tkinter import messagebox

    # THIS BASE PATH MUST MATCH THE SERVER'S CONFIGURATION FOR THE STORAGE DIRECTORY
    # It should ideally be read from a config file or environment variable shared with the main app.
    AUTHORITATIVE_STORAGE_BASE_PATH = "Z:\\3DPrintFiles\\storage\\" # Example: Use a raw string or escaped backslashes

    def log_message(message):
        # Basic logging to a local file. In a real app, use Python's logging module.
        print(f"LOG: {message}") # Replace with actual file logging
        # with open("SlicerOpener.log", "a") as log_file:
        #     log_file.write(f"{datetime.datetime.now()}: {message}\n")

    def show_error_popup(title, message):
        log_message(f"ERROR_POPUP: {title} - {message}")
        # This is a placeholder for a GUI popup.
        # tkinter.Tk().withdraw() # Hide the main tkinter window
        # messagebox.showerror(title, message)
        print(f"ERROR_UI: {title} - {message}") # Fallback for non-GUI environments

    def open_in_slicer(uri):
        log_message(f"Received URI: {uri}")
        parsed_url = urlparse(uri)
        query_params = parse_qs(parsed_url.query)
        file_path_from_url = query_params.get('path', [None])[0]

        if not file_path_from_url:
            show_error_popup("Error", "No file path found in URL.")
            log_message("Validation failed: No file path in URL.")
            return

        log_message(f"Extracted file path from URL: {file_path_from_url}")

        try:
            # Security validation:
            # 1. Normalize and make absolute
            normalized_path = os.path.normpath(file_path_from_url)
            abs_file_path = os.path.abspath(normalized_path)
            log_message(f"Normalized and absolute path: {abs_file_path}")

            # 2. Check if it starts with the authoritative base path (case-insensitive for Windows)
            # This is a critical security check.
            if not abs_file_path.lower().startswith(AUTHORITATIVE_STORAGE_BASE_PATH.lower()):
                error_msg = f"Security validation failed. Path '{file_path_from_url}' (resolved to '{abs_file_path}') is outside the allowed storage area ('{AUTHORITATIVE_STORAGE_BASE_PATH}')."
                show_error_popup("Security Error", error_msg)
                log_message(error_msg)
                return
            
            log_message("Security validation passed.")

            # Path seems okay, proceed to open
            # Ensure the file exists before attempting to open
            if not os.path.exists(abs_file_path):
                error_msg = f"File not found: {abs_file_path}"
                show_error_popup("File Error", error_msg)
                log_message(error_msg)
                return

            slicer_exe_path = "C:\\Program Files\\PrusaSlicer\\prusa-slicer.exe" # Example
            log_message(f"Attempting to open: {abs_file_path} with slicer: {slicer_exe_path}")
            subprocess.run([slicer_exe_path, abs_file_path], check=True)
            log_message(f"Successfully launched slicer for: {abs_file_path}")
        except FileNotFoundError:
            error_msg = f"Slicer executable not found at {slicer_exe_path}"
            show_error_popup("Slicer Error", error_msg)
            log_message(error_msg)
        except Exception as e:
            error_msg = f"Error opening {abs_file_path} in slicer: {e}"
            show_error_popup("Opening Error", error_msg)
            log_message(error_msg) # Log to a file for troubleshooting

3.  **Web Dashboard Integration**:
    *   The "Open File" button in the dashboard generates the `3dprint://` link dynamically using `job.file_path`.
    ```html
    <a href="3dprint://open?path={{ job.file_path|urlencode }}">Open in Slicer</a>
    ```

## 5. Operational Considerations

### 5.1 Implementation Phases
1.  **Basic Structure**: Flask app, DB setup, core `Job` model, basic file structure.
2.  **Shared Infrastructure**: Setup shared network storage, decide on DB strategy.
3.  **Student Submission**: Implement public upload form, validation, file saving to "Uploaded" (with renaming).
4.  **Staff Dashboard (View Only)**: Basic staff login, display jobs from "Uploaded" status.
5.  **Staff Approval/Rejection**: Implement modals, backend logic to move to "Pending" or "Rejected", initial email notifications.
6.  **Student Confirmation**: Token generation, confirmation page, move to "ReadyToPrint".
7.  **Printing Workflow**: Implement "Mark Printing", "Mark Complete", "Mark Picked Up" status changes and file movements.
8.  **Custom Protocol Handler**: Develop and test `SlicerOpener.py` (including robust security validation, user-facing error handling, and local file access logging) and registry setup. Integrate "Open File" button.
9.  **Thumbnails & UI Polish**: Implement thumbnail generation, refine dashboard UI with Alpine.js.
10. **Admin Controls**: Implement manual override features.
11. **Metrics & Reporting**: Add basic reporting features.
12. **Testing & Refinement**: Comprehensive testing throughout.

### 5.2 Security Considerations
-   Secure file upload handling (type validation, `secure_filename`, size limits).
-   Time-limited, cryptographically signed tokens for student confirmation.
-   Staff password storage (if using a more complex auth in future) should use strong hashing (e.g., bcrypt via `passlib`). For shared password, store securely in config.
-   CSRF protection for all forms (Flask-WTF).
-   Ensure network share has appropriate read/write permissions for the app server, but restricted for general users.
-   Validate all file paths before use to prevent path traversal attacks.
-   Regularly update dependencies.
-   Content Security Policy (CSP) headers.

### 5.3 Deployment Considerations
1.  **Network Setup**: As per section 4.1.1.
2.  **Application Deployment**:
    *   Flask application typically runs on one computer acting as the server.
    *   Use a production-ready WSGI server (e.g., Waitress, Gunicorn).
    *   Other computers access the web interface via browser.
    *   Protocol handler and helper app (`SlicerOpener.exe`) must be deployed on all staff computers that need to open files.
    *   Ensure required slicer software is installed on staff computers.
3.  **Path Consistency**: Critical. Use UNC paths in configuration and database where possible if mapped drives vary, or ensure identical mapped drives.
*   **Basic Error Logging**: The Flask application should be configured for basic error logging (e.g., using Python's `logging` module). Logs should capture unhandled exceptions and important application events, writing them to a file with timestamps. This provides essential information for troubleshooting. Advanced monitoring or alerting features are out of scope for this simple system.
*   **Email Deliverability Considerations**: While the application will handle sending emails via Flask-Mail using configured SMTP credentials, aspects like setting up SPF/DKIM DNS records to improve email deliverability are considered operational tasks for the email server administrator and are external to this application's development scope.

### 5.4 University Network Considerations
-   **Firewalls**: May block custom protocols or outgoing connections for the helper app. Liaise with IT.
-   **Server Restrictions**: University IT may have policies against running persistent servers or specific ports.
-   **Admin Rights**: Registering protocol handlers or installing software might require admin rights. The helper app can be deployed to user-space if packaged correctly.
-   **Storage Quotas**: Be mindful of file sizes and implement cleanup if quotas are restrictive.
-   **Alternative File Access**: If custom protocol is unfeasible, a fallback could be instructing staff to copy a displayed network path, or a less ideal "download and open".

### 5.5 Cost Matrix & Calculation
```python
PRINTERS = { # This can be moved to config or a simple DB table
    "Prusa MK4S":  {"rate_g": 0.08, "rate_min": 0.01, "type": "Filament"},
    "Prusa XL":    {"rate_g": 0.09, "rate_min": 0.011, "type": "Filament"},
    "Raise3D":     {"rate_g": 0.10, "rate_min": 0.012, "type": "Filament"},
    "Formlabs":    {"rate_g": 0.12, "rate_min": 0.008, "type": "Resin"},
}

def calculate_cost(printer_name: str, weight_g: float, time_min: int) -> Decimal:
    # In a real app, PRINTERS might come from config or DB
    printer_config = PRINTERS.get(printer_name)
    if not printer_config:
        raise ValueError(f"Unknown printer: {printer_name}")
    cost = Decimal(weight_g * printer_config["rate_g"]) + Decimal(time_min * printer_config["rate_min"])
    return cost.quantize(Decimal("0.01")) # Format to 2 decimal places
```
The student submission form will offer "Print Method" (Filament/Resin). Staff will select the specific printer from the dashboard when approving, which then drives cost. The system logic that calculates and saves `job.cost_usd` (after staff input weight and time) must also enforce the $3.00 minimum charge acknowledged by the student during submission (e.g., by taking the maximum of the calculated cost and $3.00).

### 5.6 Metrics & Reporting
1.  **Usage Statistics**:
    *   Dashboard overview: Daily/weekly/monthly submission counts.
    *   Trends: Peak usage times, job completion rates.
2.  **Printer Utilization**:
    *   Rate by printer model, material usage, average job duration.
3.  **Reporting Interface**:
    *   (Future) CSV/Excel export, filterable views, basic charts.

### 5.7 Data Retention and Cleanup Policy
-   **Retention Period:** Job data (database records) and associated files (original uploads, sliced files, thumbnails) for jobs in a final state ("Completed," "PaidPickedUp," or "Rejected") will be retained for a standard period of **90 days** from the date the job reached that final status.
-   **Cleanup Process:** Initially, cleanup will be a **manual process**. Staff will be responsible for periodically identifying and deleting jobs and their associated files that are older than the retention period.
-   **Active Jobs:** Jobs in "Uploaded," "Pending," "ReadyToPrint," or "Printing" statuses are considered active and are not subject to this cleanup policy until they reach a final state.
-   **Future Enhancement:** Automated cleanup scripts or features are considered a future enhancement, not part of the initial simple system.

### 5.8 Backup and Disaster Recovery
To protect against data loss, the following manual backup procedures are recommended:
-   **SQLite Database File (`app.db`):**
    -   If the `app.db` file is stored on the local disk of the designated server computer, staff should manually copy this file to a separate, secure backup location (e.g., external drive, different network share) on a regular basis (e.g., weekly, or before/after significant system maintenance).
    -   If `app.db` is stored on a network share that is already subject to regular, automated backups by IT, these IT backups can be relied upon for the database.
-   **File Storage (`storage/` directory):**
    -   Staff should manually copy the entire `storage/` directory (containing all uploaded files, sliced files, and thumbnails) to a separate, secure backup location on a regular basis.
    -   If the `storage/` directory is stored on a network share that is already subject to regular, automated backups by IT, these IT backups can be relied upon for the file storage.

### 5.9 Development Implementation Lessons
Critical considerations discovered during development that must be incorporated:

#### 5.9.1 Windows Development Environment
-   **PowerShell Compatibility**: Windows PowerShell doesn't support the `&&` operator for command chaining; use semicolon (`;`) instead
-   **Path Handling**: Use proper Windows path separators and be mindful of UNC path compatibility

#### 5.9.2 Flask-WTF Integration Requirements
-   **Essential Dependency**: Flask-WTF is critical for form handling, CSRF protection, and file upload validation
-   **Form Architecture**: SubmissionForm class must include proper validators (DataRequired, Email, Length, custom FileSizeLimit)
-   **Template Integration**: Forms require `{{ form.hidden_tag() }}` for CSRF tokens and proper field rendering

#### 5.9.3 Template Management Best Practices
-   **Readable Formatting**: Maintain proper indentation and structure in Jinja2 templates to avoid syntax errors
-   **Jinja2 Syntax**: Avoid invalid characters like `#` in template expressions; use proper Jinja2 filter syntax
-   **Filter Validation**: Ensure all Jinja2 filters exist before use (e.g., `date` filter requires additional imports)

#### 5.9.4 JavaScript Implementation Patterns
-   **File Validation**: Use File API for client-side file size and type validation before upload
-   **Dynamic Form Behavior**: Implement proper state management for dependent form fields (print method → color selection)
-   **Error Handling**: Provide immediate visual feedback for form validation errors with proper CSS classes
-   **State Management**: Track form states (loading, error, disabled) for better user experience

#### 5.9.5 Form UX Requirements
-   **Progressive Enhancement**: Start with accessible HTML forms and enhance with JavaScript
-   **Error Recovery**: Provide clear error messages and preserve form state on validation failures
-   **Visual Feedback**: Use consistent color coding (red borders) and iconography for error states
-   **Loading States**: Show loading indicators during form submission to prevent double-submission