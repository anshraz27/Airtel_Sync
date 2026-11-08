# 🏆 Airtel SYNC — Project Udyam Digital (Track A: Enterprise)
### *Making 6 Crore+ Indian MSMEs Go Digital in One Sitting*

---

## 📌 Executive Overview
This repository contains the complete, production-grade hackathon prototype and business case for **Airtel SYNC (Enterprise Track A: Project Udyam Digital)**. It transforms the slow, paper-heavy, 17.6-day acquisition process of Accel Business into a **sub-5-minute, self-serve digital onboarding journey on a phone in vernacular languages**.

---

## 🚀 Quickstart: Launching the Prototype

### 1. Requirements
- Python 3.10+
- All dependencies installed (`fastapi`, `uvicorn`, `scikit-learn`, `pillow`, `pydantic`, `pandas`, `python-pptx`)

### 2. Start the Server
Run the unified FastAPI server:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open your browser or mobile browser simulation at:
👉 **`http://localhost:8000`**

Interactive API Docs (Swagger):
👉 **`http://localhost:8000/docs`**

---

## 🛠️ Architecture & Ponytail Engineering Highlights
Built adhering strictly to the **Ponytail** engineering philosophy: *lazy senior dev mode — YAGNI, standard library where possible, zero avoidable boilerplate, deterministic guards around AI, and maximum demo impact.*

1. **Free Hugging Face AI Stack**:
   - **Primary LLM**: `Qwen/Qwen2.5-72B-Instruct` or `meta-llama/Llama-3.3-70B-Instruct` via Hugging Face Serverless Inference API (Free tier).
   - **HF Alternatives**: `deepseek-ai/DeepSeek-R1-Distill-Qwen-32B`, `meta-llama/Llama-3.1-8B-Instruct`, `mistralai/Mistral-7B-Instruct-v0.3`.
   - **KYC Vision / OCR**: `Qwen/Qwen2-VL-7B-Instruct` / `meta-llama/Llama-3.2-11B-Vision-Instruct` (with alternatives `microsoft/trocr-base-printed`, `naver-clova-ix/donut-base`).
   - **Deterministic Fallback**: Built-in offline rule engine ensures **100% demo uptime and resilience** even if Hugging Face experiences serverless rate limits or network issues in front of judges!

2. **Smart KYC & Planted Trap Defenses**:
   - **K01**: Catches blank/missing Udyam registration number + Cancelled GSTIN status in mock registry.
   - **K02**: Detects skewed/rotated document canvas; automatically applies orientation correction.
   - **K04**: Calculates edge variance sharpness (175.8 vs 300 cutoff) to detect and flag blurry, degraded images.
   - **K05**: Cross-checks entity names across documents; detects mismatch between GST Trade Name and Electricity Bill entity.
   - **90-Day Freshness Check**: Strictly enforces the address proof validity window against the hackathon reference date (`2026-07-15`).
   - **Checksum Validation**: Implements full Indian GSTIN Mod-36 checksum validator accepting `X` as the 4th character of PAN.

3. **Field Force & Channel Partner Integration (Stretch Goal)**:
   - Scikit-learn Logistic Regression trained on 5,000 leads (`smb_leads.csv`, ROC-AUC: 0.69).
   - Generates conversion propensity scores (0-100%) and delivers a **Warm Recovery Queue** for sales partners with pre-filled context and customized discount hooks.

4. **DPDP Act, 2023 Compliance**:
   - Explicit unbundled pre-KYC consent screen.
   - Zero raw PII storage; automated identifier masking in UI and logs (e.g., `37IHK*****L1ZS`).
   - 30-day automated document retention policy.

---

## 📂 Repository Deliverables Inventory

| File | Description |
|---|---|
| `app/main.py` | Unified FastAPI application serving REST API and Mobile-First Tailwind SPA. |
| `app/advisor.py` | Conversational needs advisor with Free Hugging Face LLM integration and Hindi/English support. |
| `app/eligibility.py` | Deterministic eligibility engine checking city tier, size, GSTIN, and dependency rules. |
| `app/kyc.py` | Smart KYC pipeline with Hugging Face Vision, planted trap detection, and DPDP compliance. |
| `app/quote.py` | Interactive quote engine calculating transparent pricing, GST, and bundle discounts. |
| `app/orders.py` | Order provisioning service with dynamic milestone tracker and SLA-based activation dates. |
| `app/propensity.py` | ML model scoring inbound leads and prioritizing unclosed prospects for field partners. |
| `app/registries.py` | Mock GSTIN (3,534 records) and Udyam (2,723 records) lookup APIs with Mod-36 checksum validator. |
| `privacy_note.md` | Mandatory 1-page Data Privacy & Security Architecture Note under DPDP Act 2023. |
| `Airtel_SYNC_Udyam_Digital_Submission.pptx` | 10-slide business case presentation built from official hackathon template. |
| `hackathon_strategy.md` | Comprehensive 7-step hackathon battle plan, judging criteria mapping, and judge Q&A prep. |

---

## 📊 Business Impact Summary

| Metric | Current Baseline (smb_leads.csv) | Project Udyam Digital Target |
|---|---|---|
| **Lead-to-Activation Conversion** | 7.4% | **15.0%+ (2x lift)** |
| **Turnaround Time (Lead to Activation)** | 17.6 days | **<= 5 days (wireless) / <= 7 days (fibre)** |
| **Blended Customer Acquisition Cost (CAC)** | ₹15,000 / activated SMB | **<= ₹5,000 / activated SMB (3x lower)** |
| **Customer Status Chase Calls** | 3.0 calls / lead | **< 0.2 calls / lead (Order Tracker)** |
| **Customer Monthly Savings** | Fragmented vendors | **30 - 35% consolidated savings** |

