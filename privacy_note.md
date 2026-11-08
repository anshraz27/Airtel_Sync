# Airtel SYNC — Project Udyam Digital
## 1-Page Data Privacy & Security Architecture Note (DPDP Act, 2023 Compliance)

### 1. Executive Summary & Regulatory Stance
Project Udyam Digital is designed from the ground up to comply with the **Digital Personal Data Protection (DPDP) Act, 2023** of India. Small business onboarding frequently involves sensitive commercial and personal identifiers (PAN, GSTIN, Aadhaar, electricity consumer numbers, signatory identity). Our architecture establishes strict purpose limitation, data minimisation, and storage limitation controls.

---

### 2. Core Privacy Principles Implemented

#### A. Lawful Processing & Explicit Consent Architecture (Section 6, DPDP Act)
- **Granular, Pre-KYC Consent Gate**: Before any document upload or registry query occurs, the business owner must review and accept an unbundled, plain-language consent screen available in their preferred language (English/Hindi).
- **Consent Artifact Storage**: Each consent event is stored with a cryptographic SHA-256 hash containing: `Timestamp (UTC)`, `User IP/Session ID`, `Document Scope`, and `Specific Notice Version`.
- **Purpose Limitation**: Consent is strictly bound to: *(1) Enterprise broadband feasibility verification*, *(2) Identity verification against national registries*, and *(3) Single billing account creation*. Data is never repurposed for third-party commercial marketing without independent consent.

#### B. Data Minimisation & Zero-Storage of Raw Identity Artifacts (Section 8, DPDP Act)
- **Selective Field Extraction**: The Hugging Face Vision OCR and document verification pipeline only extracts the minimal viable attributes required for telecom activation:
  - *GST Certificate*: GSTIN, Legal Name, Status. (Financial turnover details are ignored).
  - *Address Proof (Electricity Bill)*: Consumer Number, Billed Entity Name, Bill Date (for the 90-day freshness rule). Power consumption unit history is discarded in memory.
  - *Signatory ID*: Name, Validity Date. Unnecessary biometric or personal background elements are zeroed out.
- **Ephemeral Processing**: Uploaded document images are processed in-memory or in an encrypted temporary enclave (`/tmp/kyc_enclave`) with strict permissions and shredded upon verification completion.

#### C. Identifier Masking in Logs, Telemetry, and UI (Section 8, DPDP Act)
- **Strict Masking Middleware**: No raw PAN, GSTIN, or consumer identifiers are ever logged to application stdout, audit trails, or unauthenticated UI views.
  - *Format*: First 3 characters and last 3 characters visible; center masked (e.g., `37IHK*****L1ZS`).
- **Telemetry Sanitisation**: Error tracking and APM traces strip all query string identifiers and request payloads containing taxpayer records.

#### D. Storage Limitation & Automated Retention Policy (Section 8(7), DPDP Act)
- **30-Day Automated Deletion**: In accordance with telecom customer acquisition norms, customer KYC document artifacts are permanently deleted **30 days** following successful installation and activation.
- **Unclosed Leads Right to be Forgotten**: Leads that drop off in the advisor phase and do not activate have their temporary drafts purged after **14 days**, leaving only anonymised aggregate funnel telemetry for drop-reason analytics.

---

### 3. Security Architecture & Threat Defenses

| Risk / Attack Surface | Technical Safeguard Implemented |
|---|---|
| **Man-in-the-Middle (MitM) Interception** | TLS 1.3 enforced for all client-to-API and API-to-Hugging Face inference router communications. |
| **Tampered / Skewed Documents** | Automated canvas skew detection and edge-variance Laplacian sharpness validation (rejects blurry uploads < 300 score; corrects skew). |
| **Cancelled / Fraudulent GSTINs** | Real-time cross-validation against official GST registry; flags 'Cancelled' and 'Suspended' statuses immediately before quote binding. |
| **Insider Access / Data Leakage** | Role-Based Access Control (RBAC): Field sales partners only see propensity scores and business names in the back-office queue; full document records remain restricted to the automated verification engine. |

*Signed: Lead Security & Privacy Architect · Project Udyam Digital · October 2026*

