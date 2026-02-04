# AI Governance: Senior Auditor Coach

OnTrackIA integrates AI as a regulatory gatekeeper to ensure the quality and depth of technical documentation.

## 🧠 Senior Auditor Coach Persona

The AI Service (Mistral-powered) operates under the **Senior Auditor Coach** persona, which enforces standards derived from **ICAO Doc 9859** (Safety Management) and the **"Dirty Dozen"** (Human Factors).

### Evaluation Logic

The AI evaluates technician descriptions based on four mandatory pillars:

1. **Rejection of Superficiality**: Rejects vague terms like "fixed component" or "replaced part".
2. **Technical Depth**: Demands identification of specific failure modes (e.g., fatigue, corrosion, localized overheating) and part numbers (P/N) when applicable.
3. **Human Factors (Dirty Dozen)**: Prevents the use of "human error" as a root cause. Must identify specific factors like Fatigue, Stress, Pressure, or Lack of Communication.
4. **Procedural Traceability**: Requires evidence that actions were performed following official manuals (AMM, SRM).

### Implementation Workflow

- **Pre-Registration Check**: The AI analyzes the `task_details` before allowing the record to be submitted.
- **Feedback Loop**: Returns a JSON object with a logic-driven "Score" (0-100) and specific auditor feedback if a rejection occurs.
- **Guardrails (`verify_ai.py`)**: A governance script that checks for LLM hallucinations or off-topic responses, ensuring the AI stays within aviation safety boundaries.
