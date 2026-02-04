# Zero Insurrections Branding Policy

The OnTrackIA platform enforces a strict nomenclature policy to ensure professional alignment and clear product identity. This policy, internally known as "Zero Insurrections," mandates the total removal of legacy and forbidden terms from all codebase, documentation, and user interfaces.

## 🚫 Forbidden Nomenclature

The following terms are strictly prohibited and must be replaced in any artifact or source file:

| Forbidden Term | Approved Replacement |
| :--- | :--- |
| **Gold** | **Stable** / **Final** / **OnTrackIA** |
| **Gold Master** | **OnTrackIA Stable** / **Final Version** |
| **Enterprise** | **OnTrackIA** / **Standard** |
| **Beta** | **Stable** / **Verified** |
| **Master** (Branding) | **Stable** / **Main** |
| **MasterPrompt** | **OnTrackIA_Prompt** |
| **MASTER_KEY** | **SYSTEM_KEY** / **ENCRYPTION_KEY** |
| **Master Key** | **System Key** / **Encryption Key** |

## 🛡️ Enforcement Strategies

### 1. Global Sanitization

Periodic deep-scans are performed to locate and purge any remnants of forbidden terms. Technical keys (like encryption keys) are renamed to neutral terms to satisfy the policy without breaking functionality.

**Comando de Auditoría Transparente:**

```bash
grep -riE "(Gold|Beta|Enterprise|Master)" . | grep -v "Binary file"
```

### 2. "Digital Typewriter" Alignment

The branding aesthetic—**Morado Oscuro** (#0a051a)—and the **Clean Block** dashboard style are the only authorized visual identities. Any deviation (e.g., legacy "Orange" or "Enterprise" visuals) is considered a violation of the policy.

### 3. Deployment Quarantine

Any package containing forbidden terms is denied deployment to production (Hetzner). The "Zero Insurrections" audit is a mandatory step in the Pre-Deployment Audit Certification.

## 🏛️ Policy Mandate

This policy is enforced by the **Senior Auditor Coach** and the **OnTrackIA Compliance Engine** to maintain trust with regulatory authorities (RAC/EASA) and ensuring the platform presents a unified, premium identity.
