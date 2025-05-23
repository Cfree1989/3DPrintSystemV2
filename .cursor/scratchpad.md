# 3D Print System Project Scratchpad

## Background and Motivation
This project aims to develop a Flask-based 3D print job management system tailored for an academic/makerspace environment. The core goal is to replace manual or ad-hoc systems with a centralized, digital platform that streamlines the workflow from student submission through staff approval to print completion. Key features include robust file lifecycle management (preserving original uploads while tracking sliced files), job status tracking, email notifications, thumbnail generation for previews, and a custom protocol handler to allow staff to open 3D files directly in local slicer applications from the web interface. The system is designed to support operations across two computers via a shared network storage solution and a single Flask application instance serving the system. (Ref: masterplan.md Sections 1, 2.1, 4.1)

## Key Challenges and Analysis
1.  **Multi-Computer File & Database Access:** Ensuring consistent and reliable file access across two computers via shared network storage (`masterplan.md` Section 4.1.1) and managing the SQLite database access through a single server instance to prevent corruption (`masterplan.md` Section 4.1.2). The choice of a single Flask server simplifies database concurrency.
2.  **Direct File Opening (`SlicerOpener.py`):** Implementing the custom URL protocol (`3dprint://`) and the `SlicerOpener.py` helper application (`masterplan.md` Section 4.2, 4.3).
    *   **Security:** Requires robust security validation within `SlicerOpener.py` to strictly ensure only files within designated shared storage subdirectories can be opened, preventing path traversal or other unauthorized file access. This is a V1 priority.
    *   **Error Handling & User Feedback:** `SlicerOpener.py` must provide clear, user-facing error messages (e.g., via simple GUI popups) for issues like file not found, network errors, access denied, or security validation failures. This is a V1 priority.
    *   **Logging:** `SlicerOpener.py` should perform basic local logging of file access attempts (URI received, success/failure, reason for failure). This is a V1 priority.
    *   **Network Dependency:** The feature inherently depends on a stable network connection to the shared storage. Offline access is out of scope for V1; manual file copying is the fallback if the network or protocol handler fails. This is an accepted V1 trade-off.
    *   **File Locking/Concurrency:** True file locking to prevent simultaneous edits by different staff members is complex. Given the anticipated workflow and small team size, this is a V2 consideration. Slicer software might offer some inherent protection, but this is not guaranteed. The risk of data overwrite in V1 is low but acknowledged.
    *   **Installation & Updates:** `SlicerOpener.py` and its associated protocol registration require manual installation on each staff computer. Updates will also be manual for V1.
3.  **File Lifecycle Management:** Accurately tracking original student uploads versus staff-modified/sliced files, ensuring the correct "authoritative" file is used at each job stage, and managing file movements between status-based directories (e.g., `Uploaded/`, `Pending/`, `ReadyToPrint/`) (`masterplan.md` Section 3.4). Standardized file naming is crucial.
4.  **Email Notifications & Student Confirmation:** Implementing reliable email sending for various job stages and managing the token-based student confirmation workflow for print jobs (`masterplan.md` Sections 2.1, 3.3, 3.4).
5.  **Thumbnail Generation:** Integrating a library like Trimesh for thumbnail generation and gracefully handling potential failures (`masterplan.md` Section 2.1, 3.1 services/thumbnail_service.py).
6.  **Deployment & Configuration:** Ensuring path consistency for shared storage across machines and correctly deploying the Flask app, WSGI server, and the `SlicerOpener.py` tool (`masterplan.md` Section 5.3).
7.  **User Interface for Complex Workflow:** Designing clear UIs for student submission, staff dashboard interactions (including modals for approval/rejection), and administrative overrides (`masterplan.md` Section 3.4 UI/UX descriptions).

## High-level Task Breakdown
(Derived from masterplan.md Section 5.1 Implementation Phases)

1.  **Task 1: Initial Project Setup & Basic Structure** (Ref: masterplan.md Section 5.1.1)
    *   Create Flask application structure (app factory, config, extensions).
    *   Initialize database (SQLAlchemy, SQLite) and `Job` model (as per masterplan.md Section 3.2).
    *   Set up basic file storage directories (`storage/Uploaded`, `Pending`, etc. as per masterplan.md Section 3.1).
    *   Implement `requirements.txt`.
    *   Success Criteria: Basic Flask app runs, database schema created, storage directories exist. `Job` model can be interacted with via Flask shell.
2.  **Task 2: Shared Infrastructure Configuration** (Ref: masterplan.md Section 5.1.2)
    *   Define and document shared network storage setup requirements (e.g., mapped drive letter or UNC path).
    *   Confirm database strategy (single server instance for Flask app with SQLite).
    *   Success Criteria: Configuration for shared storage path is defined in `app/config.py`. Documentation outlines how staff computers should be configured for shared access.
3.  **Task 3: Student Submission Module** (Ref: masterplan.md Section 5.1.3, 3.4 Student Submission UI/UX)
    *   Implement public upload form (`/submit`) with fields as specified.
    *   Implement client-side and server-side validation for form data and file uploads (type, size).
    *   Implement file saving to `storage/Uploaded/` with standardized renaming convention.
    *   Implement thumbnail generation upon successful upload (`thumbnail_service.py`).
    *   Implement success page (`/submit/success`).
    *   Success Criteria: Students can submit a job, file is saved correctly with standardized name, thumbnail is generated (or fails gracefully), job record created in DB with 'UPLOADED' status.
4.  **Task 4: Staff Dashboard - Basic View & Login** (Ref: masterplan.md Section 5.1.4, 3.4 General Staff Dashboard)
    *   Implement basic staff login (shared password defined in config).
    *   Create staff dashboard page (`/dashboard`) displaying jobs with "UPLOADED" status.
    *   Implement basic job row details display.
    *   Success Criteria: Staff can log in. Dashboard lists jobs from "UPLOADED" status.
5.  **Task 5: Staff Approval & Rejection Workflow** (Ref: masterplan.md Section 5.1.5, 3.4 Staff Approval/Rejection UI/UX)
    *   Implement modals for job approval (with cost calculation inputs) and rejection (with reasons).
    *   Implement backend logic for:
        *   Updating job status to "PENDING" or "REJECTED".
        *   Moving files from `storage/Uploaded/` to `storage/Pending/` (if approved and sliced) or archiving/managing rejected files.
        *   Updating `job.file_path` and `job.display_name` if sliced file becomes authoritative.
        *   Calculating and storing `job.cost_usd` (enforcing minimum charge).
        *   Generating `confirm_token` for approved jobs.
    *   Implement initial email notifications for approval (pending confirmation) and rejection (`email_service.py`).
    *   Success Criteria: Staff can approve or reject jobs. Files are moved correctly. Emails are sent. Job status and relevant fields updated in DB.
6.  **Task 6: Student Confirmation Workflow** (Ref: masterplan.md Section 5.1.6, 3.4 Pending & ReadyToPrint statuses)
    *   Implement confirmation page linked from approval email.
    *   Implement token validation logic.
    *   Implement backend logic to update job status to "READYTOPRINT" upon successful confirmation.
    *   Implement file movement from `storage/Pending/` to `storage/ReadyToPrint/`.
    *   Update `job.student_confirmed`, `job.student_confirmed_at`.
    *   (Optional) Email to student confirming job is in queue.
    *   Success Criteria: Student can confirm job via email link. Job status updates to "READYTOPRINT", file moves to correct directory.
7.  **Task 7: Printing Workflow (Printing, Completed, PaidPickedUp)** (Ref: masterplan.md Section 5.1.7, 3.4 Printing, Completed, PaidPickedUp statuses)
    *   Implement staff actions to "Mark Printing", "Mark Complete", "Mark Picked Up".
    *   Implement backend logic for status changes and corresponding file movements between `storage/ReadyToPrint/`, `storage/Printing/`, `storage/Completed/`, `storage/PaidPickedUp/`.
    *   Implement email notification for job completion.
    *   Success Criteria: Staff can transition jobs through Printing, Completed, PaidPickedUp statuses. Files are moved. Completion email sent.
8.  **Task 8: Custom Protocol Handler & "Open File" Feature** (Ref: masterplan.md Section 5.1.8, 4.2, 4.3)
    *   Develop `SlicerOpener.py` script, including robust security validation (preventing path traversal and ensuring files are within the authoritative storage base path), clear user-facing error handling (e.g., GUI popups for errors like file not found, access denied, validation failure), and basic local file logging of access attempts (success/failure).
    *   Document registry setup for `3dprint://` protocol (e.g., provide a `.reg` file and manual instructions).
    *   Integrate "Open File" button in staff dashboard to generate `3dprint://` links.
    *   Success Criteria: `SlicerOpener.py` successfully opens files from the designated shared storage in the appropriate slicer software when called via the `3dprint://` protocol. Path validation in the script prevents unauthorized access and provides clear error feedback to the user. Access attempts (successes and failures with reasons) are logged locally by `SlicerOpener.py`.
9.  **Task 9: UI Polish & Advanced Features** (Ref: masterplan.md Section 5.1.9)
    *   Refine dashboard UI/UX using Alpine.js for interactivity (status tabs, modals).
    *   Improve thumbnail display and error handling.
    *   Implement full Job Detail View/Modal.
    *   Success Criteria: Dashboard is interactive and user-friendly. All job details are viewable and editable as specified.
10. **Task 10: Administrative Controls** (Ref: masterplan.md Section 5.1.10, 3.4 Administrative Controls UI/UX)
    *   Implement manual status override controls.
    *   Implement file management controls (upload new version, download).
    *   Implement option to send/suppress emails during manual overrides.
    *   Success Criteria: Staff can perform administrative actions as specified in `masterplan.md`.
11. **Task 11: Metrics & Reporting (Basic)** (Ref: masterplan.md Section 5.1.11, 5.6)
    *   Implement basic dashboard stats (e.g., submission counts).
    *   Success Criteria: Basic usage statistics are displayed on the dashboard.
12. **Task 12: Comprehensive Testing & Refinement** (Ref: masterplan.md Section 5.1.12)
    *   Conduct end-to-end testing of all features.
    *   Address bugs and refine based on testing.
    *   Success Criteria: System is stable and meets requirements defined in `masterplan.md`.

## Project Status Board
(Executor to update with progress using Markdown TODO format: - [ ] Task Name)

- [x] Task 1: Initial Project Setup & Basic Structure
- [x] Task 2: Shared Infrastructure Configuration
- [ ] Task 3: Student Submission Module
    - [x] Implement public upload form (`/submit`) with fields as specified.
    - [x] Implement client-side and server-side validation for form data and file uploads (type, size).
    - [x] **RESOLVED**: Fix template error in base.html preventing form display
    - [ ] **CURRENT**: Comprehensive Form Field Updates & Enhancements
        - [x] Phase 1: Update discipline options to match actual program offerings
        - [x] Phase 1: Add form introduction text (user-specified exact wording)
        - [x] Phase 1: Add print method context descriptions (Resin vs Filament)
        - [x] Phase 1: Implement dynamic color selection (23 filament + 4 resin colors)
        - [ ] Phase 2: Enhanced scaling question with printer specifications
        - [ ] Phase 2: Class number format validation (ARCH 4000 pattern)
        - [ ] Phase 3: Comprehensive testing of all form enhancements
    - [ ] Implement file saving to `storage/Uploaded/` with standardized renaming convention.
    - [ ] Implement thumbnail generation upon successful upload (`thumbnail_service.py`).
    - [ ] Implement success page (`/submit/success`).
    - [ ] **Task 3.6: Form Enhancements Phase 2** (DEFERRED after core functionality)
        - [ ] Enhanced scaling question with comprehensive printer specifications
        - [ ] Class number format validation (ARCH 4000 pattern with regex)
        - [ ] Allow "N/A" for non-academic projects in class number field
        - [ ] Add scaling guidance and STL/OBJ export warnings
        - [ ] Require explicit acknowledgment of dimensional constraints
        - [ ] Comprehensive testing of Phase 2 enhancements
        - Success Criteria: Enhanced scaling question captures meaningful responses, class number validation enforces correct format, user experience flows smoothly through all form enhancements
4.  **Task 4: Staff Dashboard - Basic View & Login** (Ref: masterplan.md Section 5.1.4, 3.4 General Staff Dashboard)
    *   Implement basic staff login (shared password defined in config).
    *   Create staff dashboard page (`/dashboard`) displaying jobs with "UPLOADED" status.
    *   Implement basic job row details display.
    *   Success Criteria: Staff can log in. Dashboard lists jobs from "UPLOADED" status.
5.  **Task 5: Staff Approval & Rejection Workflow** (Ref: masterplan.md Section 5.1.5, 3.4 Staff Approval/Rejection UI/UX)
    *   Implement modals for job approval (with cost calculation inputs) and rejection (with reasons).
    *   Implement backend logic for:
        *   Updating job status to "PENDING" or "REJECTED".
        *   Moving files from `storage/Uploaded/` to `storage/Pending/` (if approved and sliced) or archiving/managing rejected files.
        *   Updating `job.file_path` and `job.display_name` if sliced file becomes authoritative.
        *   Calculating and storing `job.cost_usd` (enforcing minimum charge).
        *   Generating `confirm_token` for approved jobs.
    *   Implement initial email notifications for approval (pending confirmation) and rejection (`email_service.py`).
    *   Success Criteria: Staff can approve or reject jobs. Files are moved correctly. Emails are sent. Job status and relevant fields updated in DB.
6.  **Task 6: Student Confirmation Workflow** (Ref: masterplan.md Section 5.1.6, 3.4 Pending & ReadyToPrint statuses)
    *   Implement confirmation page linked from approval email.
    *   Implement token validation logic.
    *   Implement backend logic to update job status to "READYTOPRINT" upon successful confirmation.
    *   Implement file movement from `storage/Pending/` to `storage/ReadyToPrint/`.
    *   Update `job.student_confirmed`, `job.student_confirmed_at`.
    *   (Optional) Email to student confirming job is in queue.
    *   Success Criteria: Student can confirm job via email link. Job status updates to "READYTOPRINT", file moves to correct directory.
7.  **Task 7: Printing Workflow (Printing, Completed, PaidPickedUp)** (Ref: masterplan.md Section 5.1.7, 3.4 Printing, Completed, PaidPickedUp statuses)
    *   Implement staff actions to "Mark Printing", "Mark Complete", "Mark Picked Up".
    *   Implement backend logic for status changes and corresponding file movements between `storage/ReadyToPrint/`, `storage/Printing/`, `storage/Completed/`, `storage/PaidPickedUp/`.
    *   Implement email notification for job completion.
    *   Success Criteria: Staff can transition jobs through Printing, Completed, PaidPickedUp statuses. Files are moved. Completion email sent.
8.  **Task 8: Custom Protocol Handler & "Open File" Feature** (Ref: masterplan.md Section 5.1.8, 4.2, 4.3)
    *   Develop `SlicerOpener.py` script, including robust security validation (preventing path traversal and ensuring files are within the authoritative storage base path), clear user-facing error handling (e.g., GUI popups for errors like file not found, access denied, validation failure), and basic local file logging of access attempts (success/failure).
    *   Document registry setup for `3dprint://` protocol (e.g., provide a `.reg` file and manual instructions).
    *   Integrate "Open File" button in staff dashboard to generate `3dprint://` links.
    *   Success Criteria: `SlicerOpener.py` successfully opens files from the designated shared storage in the appropriate slicer software when called via the `3dprint://` protocol. Path validation in the script prevents unauthorized access and provides clear error feedback to the user. Access attempts (successes and failures with reasons) are logged locally by `SlicerOpener.py`.
9.  **Task 9: UI Polish & Advanced Features** (Ref: masterplan.md Section 5.1.9)
    *   Refine dashboard UI/UX using Alpine.js for interactivity (status tabs, modals).
    *   Improve thumbnail display and error handling.
    *   Implement full Job Detail View/Modal.
    *   Success Criteria: Dashboard is interactive and user-friendly. All job details are viewable and editable as specified.
10. **Task 10: Administrative Controls** (Ref: masterplan.md Section 5.1.10, 3.4 Administrative Controls UI/UX)
    *   Implement manual status override controls.
    *   Implement file management controls (upload new version, download).
    *   Implement option to send/suppress emails during manual overrides.
    *   Success Criteria: Staff can perform administrative actions as specified in `masterplan.md`.
11. **Task 11: Metrics & Reporting (Basic)** (Ref: masterplan.md Section 5.1.11, 5.6)
    *   Implement basic dashboard stats (e.g., submission counts).
    *   Success Criteria: Basic usage statistics are displayed on the dashboard.
12. **Task 12: Comprehensive Testing & Refinement** (Ref: masterplan.md Section 5.1.12)
    *   Conduct end-to-end testing of all features.
    *   Address bugs and refine based on testing.
    *   Success Criteria: System is stable and meets requirements defined in `masterplan.md`.

## Current Status / Progress Tracking
### Latest Planner Assessment (2024-01-XX)
**Status**: Phase 1 form enhancements successfully completed! **STRATEGIC PRIORITY SHIFT**: Moving from form polish to core functionality implementation.

**Decision Rationale**:
- ✅ **Foundation Established**: Phase 1 form enhancements provide excellent user experience baseline
- 🔄 **Core Functionality Gap**: Form cannot actually process submissions without file saving implementation
- 🎯 **End-to-End Value**: Need complete submission workflow (form → file saving → success page) for meaningful testing
- 📋 **Dependency Chain**: File saving is prerequisite for thumbnail generation and full workflow testing

**STRATEGIC PIVOT: Core Functionality Implementation Priority**

**NEXT TASK ASSIGNMENT**: **Task 3.3 - File Saving Implementation** 
*Priority: CRITICAL - Core functionality required for system operation*

### Task 3.3: File Saving Implementation Specifications

**Immediate Implementation Requirements**:
1. **Standardized File Naming Convention** (per masterplan.md Section 3.4):
   - Format: `FirstAndLastName_PrintMethod_Color_SimpleJobID.original_extension`
   - Example: `JaneDoe_Filament_Blue_123.stl`
   - SimpleJobID derived from Job.id (UUID)

2. **File Processing Workflow**:
   - Validate uploaded file (type, size) - ✅ Already implemented
   - Generate unique Job ID (UUID4)
   - Apply standardized naming convention
   - Save to `storage/Uploaded/` directory with new name
   - Update Job record with file metadata:
     - `job.original_filename` = student's upload name
     - `job.display_name` = standardized name
     - `job.file_path` = full path to saved file
     - `job.status` = 'UPLOADED'

3. **Success Criteria**:
   - ✅ Form submission creates Job record in database
   - ✅ File saved to correct directory with standardized name
   - ✅ Job metadata properly populated
   - ✅ User redirected to success page with Job ID
   - ✅ Original filename preserved in database
   - ✅ File path correctly stored for future operations

**Technical Implementation Notes**:
- Use `secure_filename()` for base filename safety
- Implement robust error handling for file I/O operations
- Ensure directory creation if `storage/Uploaded/` doesn't exist
- Generate meaningful error messages for file saving failures
- Consider file extension preservation and validation

**DEFERRED BUT IMPORTANT**:
- Phase 2 form enhancements (scaling question, class number validation) → **Task 3.6**
- Form validation testing → Will occur naturally during file saving testing

**CONFIDENCE LEVEL**: High - Flask-WTF foundation solid, file handling patterns well-established

**Flask App Status**: ✅ Confirmed working - All Phase 1 enhancements successfully integrated

## Executor's Feedback or Assistance Requests
(Executor to fill as needed with updates, questions, or blockers.)

- Task 1: Initial Project Setup & Basic Structure is complete. All directories and basic files created, database initialized with Job table, basic Flask app runs. Ready for Planner to review or assign Task 2.
- Task 2: Shared Infrastructure Configuration is complete.
    - `app/config.py` updated with `APP_STORAGE_ROOT` and `SLICER_PROTOCOL_BASE_PATH`.
    - `Config.init_app` updated to create storage subdirectories using `APP_STORAGE_ROOT`.
    - Staff setup guide created at `documentation/StaffSetupGuide.md`.
    - Database strategy (single server instance for Flask app with SQLite) confirmed as per `masterplan.md`.
  Ready for Planner to review or assign Task 3.
- Task 3.1 (Student Submission Module - Implement public upload form) is complete:
    - `app/forms.py` created with `SubmissionForm`.
    - `app/templates/main/submit.html` created to render the form.
    - `app/routes/main.py` updated for `/submit` GET/POST handling (POST is placeholder).
  The form should be viewable and basic validation messages should appear. Full submission processing is pending next sub-tasks.
  Ready for Planner to review or assign next sub-task for Task 3.
- **Task 3.2 (Client-side and Server-side Validation) is COMPLETE**:
    - Enhanced `app/forms.py` with custom `FileSizeLimit` validator (50MB max) and improved field validation
    - Enhanced `app/templates/main/submit.html` with comprehensive JavaScript client-side validation
    - All validation features implemented and tested successfully
    - Client-side validation includes real-time file validation, email format checking, form submission validation, visual error feedback, error scrolling, and loading states
    - Server-side validation includes file size limits, enhanced field validation, and improved error messages
  **Ready for Planner to assign Task 3.3 - File saving implementation**.

- **Task 3: Phase 1 Form Field Updates - COMPLETED ✅**:
    **Successfully Implemented**:
    - ✅ **Updated Discipline Options**: Replaced generic options with accurate academic programs: Art, Architecture, Landscape Architecture, Interior Design, Engineering, Hobby/Personal, Other
    - ✅ **Added Form Introduction Text**: Added comprehensive warning/guidance text at top of form using exact user-specified wording in styled yellow alert box
    - ✅ **Enhanced Print Method Context**: Added detailed descriptions for Resin vs Filament methods with cost/capability information using exact user-specified wording
    - ✅ **Dynamic Color Selection**: Implemented JavaScript-driven color dropdown that switches between 23 filament colors and 4 resin colors based on print method selection
    - ✅ **Updated Class Number Format**: Changed placeholder from "ARCH-101" to "ARCH 4000" to match user requirements
    - ✅ **Enhanced Color State Management**: Color dropdown is disabled by default and only enables after print method selection
    
    **Technical Implementation**:
    - Updated `app/forms.py` with new discipline choices and comprehensive color lists
    - Enhanced `app/templates/main/submit.html` with introduction text, print method context, and dynamic color JavaScript
    - All changes maintain existing validation framework and client-side error handling
    - Flask app creates successfully with all updates
    - **Color Selection UX**: Dropdown starts disabled with helpful text, enables with appropriate colors when print method chosen, shows color count in help text
    
    **Testing Status**: ✅ Flask app starts successfully. Form displays with new content. Color selection properly disabled until method chosen.
    
    **USER ENHANCEMENT IMPLEMENTED**: ✅ Colors are not selectable until a print method is chosen - improves UX and prevents selection of incorrect colors
    
    **GIT STATUS**: ✅ **COMMITTED AND PUSHED TO GITHUB**
    - Commit: `44f0e52` - "feat: Complete Phase 1 form enhancements with dynamic color selection"
    - Successfully pushed to origin/main
    - All Phase 1 changes now backed up and version controlled
    
    **NEXT**: Phase 2 (Enhanced scaling question with printer specifications + class number format validation) or proceed to file saving implementation per Planner decision.

## End of Day Summary - [Date]

### Today's Major Accomplishments ✅

**PHASE 1 FORM ENHANCEMENTS - FULLY COMPLETED**:
1. ✅ **Updated Academic Discipline Options** - Replaced generic options with actual program offerings
2. ✅ **Added Comprehensive Introduction Text** - Moodle guidance, scaling requirements, responsibility disclaimers
3. ✅ **Enhanced Print Method Descriptions** - Detailed Resin vs Filament context with cost/capability info
4. ✅ **Implemented Dynamic Color Selection** - 23 filament colors + 4 resin colors with smart state management
5. ✅ **Enhanced User Experience** - Color dropdown disabled until print method selected (user-requested improvement)
6. ✅ **Updated Class Number Format** - Changed example to "ARCH 4000" format
7. ✅ **Maintained Robust Validation** - All existing client/server validation preserved and enhanced

### Technical Status ✅
- ✅ **Flask App**: Creates and runs successfully
- ✅ **Dependencies**: Flask-WTF properly installed and configured
- ✅ **Templates**: Clean, properly formatted HTML with working JavaScript
- ✅ **Validation**: Comprehensive client-side and server-side validation working
- ✅ **Version Control**: All changes committed and pushed to GitHub (commit `44f0e52`)

### Next Session Priorities

**IMMEDIATE OPTIONS** (for Planner to decide):
1. **Phase 2**: Enhanced scaling question with printer specifications + class number format validation
2. **Task 3.3**: File saving implementation with standardized naming convention
3. **Task 3.4**: Thumbnail generation service implementation
4. **Task 3.5**: Success page implementation

**CURRENT BLOCKING ISSUES**: None - system is stable and ready for next development phase

**PREPARATION FOR NEXT SESSION**:
- Form foundation is solid and user-tested
- All Phase 1 requirements met and backed up
- Ready to proceed with either Phase 2 enhancements or core functionality (file saving)
- Flask development environment confirmed working

## Lessons
(Record reusable information, fixes, or learnings here.)

- The `masterplan.md` file located at the root of the project `/c%3A/3DPrintSystemV2/.cursor/masterplan.md` is the primary source of truth for project scope and requirements.
- When in doubt, refer to the custom instructions regarding Planner/Executor roles and scratchpad updates.
- User Specified Lessons:
    - Include info useful for debugging in the program output.
    - Read the file before you try to edit it.
    - If there are vulnerabilities that appear in the terminal, run npm audit before proceeding
    - Always ask before using the -force git command
- **Flask-WTF Dependency Critical**: Flask-WTF must be included in requirements.txt and installed for forms to work. Missing this causes import errors and prevents form functionality.
- **PowerShell && Operator**: PowerShell doesn't support `&&` operator like bash. Use semicolon `;` or separate commands.
- **requirements.txt Formatting**: Be careful with requirements.txt line endings. Search/replace can corrupt the file if not done carefully.
- **Flask-WTF Forms Need App Context**: When testing Flask-WTF forms in Python CLI, wrap in `with app.app_context():` to avoid RuntimeError about working outside application context.
- **File Size Validation**: Implemented custom `FileSizeLimit` validator that seeks to end of file to get size, then resets position. This works for both uploaded files and validation.
- **Client-side File Validation**: File API provides `file.size` property for immediate file size checking and `file.name` for extension validation.
- Commit message for end of day 2023-10-27 (Tasks 2 & 3.1):
  ```
  feat: Complete Task 2 (Shared Infrastructure) & Task 3.1 (Submission Form UI)

  - Configure shared storage paths in app/config.py (APP_STORAGE_ROOT, SLICER_PROTOCOL_BASE_PATH) and update init_app to create storage directories.
  - Add StaffSetupGuide.md to documentation for shared storage setup.
  - Implement SubmissionForm in app/forms.py with all required fields and validators for student print job submissions.
  - Create app/templates/main/submit.html to render the submission form using Tailwind CSS.
  - Update /submit route in app/routes/main.py to handle GET requests for form display and initial POST request structure.
  - Correct CSS syntax in submit.html style block.
  ``` 