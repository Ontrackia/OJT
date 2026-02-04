# Forensic Integrity & SHA-256 Hashing

To ensure regulatory compliance and prevent record tampering, OnTrackIA implements a forensic seal system.

## 🔒 Cryptographic Sealing Process

Every OJT record is cryptographically sealed using SHA-256 once validated by a supervisor.

1. **Payload Generation**: A unique string is created by concatenating:
   - Trainee ID
   - Task ID (ATA Chapter)
   - Aircraft Registration
   - Task Details
   - Work Date
   - Supervisor Signature
2. **Hashing**: The payload is hashed using SHA-256.
3. **Storage**: The resulting fingerprint is stored in the `entry_hash_sha256` column.
4. **Immutability**: Once sealed, the record is locked (`is_locked = True`), preventing any downstream modifications.

## 🛡️ Real-time Integrity Verification

The system provides a specialized endpoint to detect unauthorized database alterations.

- **Endpoint**: `GET /api/ojt/verify-integrity/{person_task_id}`
- **Logic**: The backend recalculates the hash from the current database values and compares it with the stored `entry_hash_sha256`.

### Visual "Corruption" Alerts

If a checksum mismatch is detected:

- **UI Flag**: The trainee row displays an `AlertTriangle` icon with "ALERTA DE INTEGRIDAD".
- **System Action**: PDF generation is disabled for the corrupted record, and an audit alert is logged.

## 📄 PDF Traceability

The SHA-256 seal is printed on all generated certificates (AAC F1 / CAP 741) to allow for offline verification of document authenticity.
