# Staff Setup Guide: 3D Print System

This guide explains how to configure your computer to correctly access the shared files for the 3D Print Management System.

## 1. Shared Storage Overview

The 3D Print System uses a central shared network location to store all print files (student uploads, sliced files, thumbnails). It's crucial that all staff computers access this location consistently.

The main application server will access this storage directly. For staff members using the "Open File" feature in the dashboard (which opens files in your local slicer software), your computer needs to have a specific path mapped to this shared storage.

## 2. Network Share Details

*   **Main Application Shared Path (UNC):** The primary shared folder for the application data is expected to be at a UNC path similar to:
    `\\REPLACE_WITH_SERVER_NAME\REPLACE_WITH_SHARE_NAME\3DPrintSystemV2\`
    (Your IT department or system administrator will provide the exact server and share name).

*   **Required Mapped Drive for SlicerOpener:** The "Open File" feature relies on a helper tool (`SlicerOpener.py`) that expects the shared `storage` directory to be accessible via the following path:
    `Z:\3DPrintSystemV2\storage\`

## 3. Configuration Steps for Staff Computers

To ensure the "Open File" feature works correctly:

1.  **Identify the Network Share:** Confirm the correct UNC path for the `3DPrintSystemV2` project directory from your IT department or system administrator (e.g., `\\SERVER_NAME\SHARE_NAME\3DPrintSystemV2\`).

2.  **Map the Network Drive:**
    *   You need to map the network share containing the `3DPrintSystemV2` directory to the `Z:` drive on your computer.
    *   **Example:** If the full path to the `3DPrintSystemV2` project on the network is `\\PrintServer\LabShare\Apps\3DPrintSystemV2\`, you would map `\\PrintServer\LabShare\Apps\` to your `Z:` drive.
    *   **Steps to Map a Network Drive (Windows):**
        1.  Open File Explorer.
        2.  Right-click on "This PC" or "Computer".
        3.  Select "Map network drive...".
        4.  Choose `Z:` as the drive letter.
        5.  For "Folder", enter the network path that *contains* the `3DPrintSystemV2` directory (e.g., `\\PrintServer\LabShare\Apps`).
        6.  Ensure "Reconnect at sign-in" is checked.
        7.  Click "Finish".

3.  **Verify Access:**
    *   After mapping, you should be able to navigate to `Z:\3DPrintSystemV2\storage\` in File Explorer and see subfolders like `Uploaded`, `Pending`, etc.

## 4. Important Notes

*   **Consistency is Key:** This `Z:\3DPrintSystemV2\storage\` path *must* be identical on all staff computers that will use the "Open File" feature.
*   **SlicerOpener.py:** This helper tool will be installed separately. It uses the `Z:\3DPrintSystemV2\storage\` path to validate and open files.
*   **Troubleshooting:** If the "Open File" button doesn't work, the most common reasons are:
    *   The network drive `Z:` is not mapped correctly.
    *   The path `Z:\3DPrintSystemV2\storage\` does not point to the correct shared `storage` directory.
    *   The `SlicerOpener.py` tool is not installed or configured correctly.

Please contact your system administrator if you have trouble mapping the network drive or locating the correct shared path. 