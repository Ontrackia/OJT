# OnTrackIA OJT Compliance Framework - Overview

The **OnTrackIA OJT Compliance Framework** is the primary orchestration layer for aviation maintenance compliance, safety (SMS), and technical training (OJT) within the OnTrackIA ecosystem. It digitizes regulated authority processes through high-integrity data injection and a unified, professional visual identity.

## 🎯 Design Philosophy: Digital Mirror & Morado Oscuro

The system operates as a **"Digital Typewriter"**, superimposing high-integrity data onto official PDF templates while maintaining a premium **"Morado Oscuro"** branding aesthetic.

- **Non-Invasive**: Authority PDFs are used as-is, ensuring 100% visual compliance with regulatory forms.
- **Brand Identity**: Deeps backgrounds (`#0a051a`) with high-contrast Purple (`#7c3aed`) accents for headers, buttons, and active states.
- **Glassmorphism**: Translucent panels and overlays providing depth and modern aeronautical professionalism.
- **Official Branding**: Integration of official OnTrackIA logos and icons across the entire platform.

## 🚀 Strategic Pillars

1. **Forensic Integrity**: Every record is sealed with **SHA-256** forensic fingerprints, ensuring immutability.
2. **AI Governance (Senior Auditor Coach)**: AI validations for Root Cause Analysis (RCA) depth using ICAO Doc 9859 and "Dirty Dozen" logic.
3. **Offline-First PWA**: Fully operational in remote environments via IndexedDB (Dexie.js) and a robust SyncEngine logic with visual indicators.
4. **Ergonomic Design**: Clean block-style dashboard optimized for field operations with 44px minimum touch targets.
5. **Regulatory Scaling**: A scalable architecture ready for specialized modules:
   - **OJT (RAC LPTA 66)**: Current baseline for technician qualification.
   - **UAS (Drones)**: Regulatory mapping for UAV operations.
   - **Visual Scan (AI)**: Defect detection with overlay-heavy interfaces.

## ⚖️ Regulatory Standards Compliance

| Standard | Requirement | Implementation |
| :--- | :--- | :--- |
| **RAC LPTA 66** | OJT Task tracking (70% Appendix 1 coverage). | OJT Module Logic |
| **UK CAA (CAP 741)**| ATA chapter methodical registration. | Native PDF Overlay |
| **AAC (F1/F2)** | Experience certification & Forensic sealing. | Compliance Engine V2 |

## 📦 System Status

- **Source of Truth**: `~/Desktop/OnTrackIA_OJT`
- **Core Governance**: Integrated `rbac_matrix.csv`, `verify_ai.py`, and `CONFIGURACION_MULTI_LLM.md`.
- **Forensic Seal**: Active SHA-256 hashing for OJT entries and supervisor signatures.
- **RCA Coach**: Senior Auditor Persona validating technical depth.
- **Branding**: 100% "Morado Oscuro" theme consolidation.
- **Deployment**: Production environment on Hetzner server.
