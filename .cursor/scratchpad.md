# 3D Print System Project Scratchpad

## Background and Motivation
This project aims to develop a Flask-based 3D print job management system tailored for an academic/makerspace environment. The core goal is to replace manual or ad-hoc systems with a centralized, digital platform that streamlines the workflow from student submission through staff approval to print completion. Key features include robust file lifecycle management (preserving original uploads while tracking sliced files), job status tracking, email notifications, thumbnail generation for previews, and a custom protocol handler to allow staff to open 3D files directly in local slicer applications from the web interface. The system is designed to support operations across two computers via a shared network storage solution and a single Flask application instance serving the system. (Ref: masterplan.md Sections 1, 2.1, 4.1)

## Key Challenges and Analysis
1.  **Multi-Computer File & Database Access:** Ensuring consistent and reliable file access across two computers via shared network storage (`masterplan.md` Section 4.1.1) and managing the SQLite database access through a single server instance to prevent corruption (`masterplan.md` Section 4.1.2). The choice of a single Flask server simplifies database concurrency.
2.  **Direct File Opening:** Implementing the custom URL protocol (`3dprint://`) and the `SlicerOpener.py` helper application (`masterplan.md` Section 4.2, 4.3). This requires careful registry modification on staff machines and security validation within the helper script to prevent opening arbitrary files.
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
    *   Develop `SlicerOpener.py` script (including path validation).
    *   Document registry setup for `3dprint://` protocol.
    *   Integrate "Open File" button in staff dashboard to generate `3dprint://` links.
    *   Success Criteria: `SlicerOpener.py` successfully opens files in slicer when called via protocol. "Open File" button works on dashboard. Path validation in script prevents unauthorized access.
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
- [ ] Task 2: Shared Infrastructure Configuration

## Executor's Feedback or Assistance Requests
(Executor to fill as needed with updates, questions, or blockers.)

- Task 1: Initial Project Setup & Basic Structure is complete. All directories and basic files created, database initialized with Job table, basic Flask app runs. Ready for Planner to review or assign Task 2.

## Lessons
(Record reusable information, fixes, or learnings here.)

- The `masterplan.md` file located at the root of the project `/c%3A/3DPrintSystemV2/.cursor/masterplan.md` is the primary source of truth for project scope and requirements.
- When in doubt, refer to the custom instructions regarding Planner/Executor roles and scratchpad updates.
- User Specified Lessons:
    - Include info useful for debugging in the program output.
    - Read the file before you try to edit it.
    - If there are vulnerabilities that appear in the terminal, run npm audit before proceeding
    - Always ask before using the -force git command 