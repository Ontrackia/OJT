# OJT Module Implementation: RAC LPTA 66

The OJT (On-the-Job Training) module is the core component for managing maintenance technician qualifications.

## ⚖️ RAC LPTA 66 Compliance

The system enforces compliance based on the completion of tasks defined in **Appendix 1** of the regulation.

- **70% Threshold**: A trainee is marked "Compliant" only after 70% of Appendix 1 tasks are validated by a supervisor.
- **Appendix tracking**: The backend tracks `appendix_1_total` vs `appendix_1_validated` in real-time.

## 🛡️ Forensic Seals

- **Generation**: Hashes are generated upon task validation, linking trainee, task, aircraft, and supervisor.
- **Locking**: Once validated, the `is_locked` flag prevents further edits to maintain a forensic paper trail.
- **Verification**: The system can recalculate and verify seals to detect tampering.

## 📄 Automated Report Generation

Using the `PDFOverlayService`, the system generates official certificates.

- **Mapping**: JSON files define the exact (X, Y) coordinates for data injection on authority forms.
- **Signatures**: Digital signatures are embedded directly into the PDF.
- **Hanging Seal**: The SHA-256 fingerprint is printed on the certificate for external verification.

## 🛤️ Data Models

- `OJTPerson`: Trainee profile linked to a system user.
- `OJTTask`: Pre-defined tasks mapped to ATA Chapters and Appendix 1 flags.
- `OJTPersonTask`: The active assignment/execution record.
- `OJTEvidence`: Attachments (photos, logs) proving task completion.
