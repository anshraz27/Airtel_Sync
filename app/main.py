import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.registries import lookup_gstin, lookup_udyam, validate_gstin_format, validate_udyam_format
from app.eligibility import get_eligible_products, build_curated_bundle, load_catalogue
from app.advisor import generate_advisor_response, HF_PRIMARY_MODEL, HF_ALTERNATIVES
from app.kyc import verify_applicant_kyc, mask_pii
from app.quote import calculate_quote
from app.orders import create_digital_order, get_order_status
from app.propensity import predict_lead_propensity, get_unclosed_leads_queue

app = FastAPI(
    title="Airtel Udyam Digital - Track A Enterprise",
    description="Digital-first acquisition and onboarding journey for 6 Crore+ Indian MSMEs (Airtel SYNC Hackathon).",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Request Models -----------------
class AdvisorMessageRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    hf_token: Optional[str] = None
    model_name: Optional[str] = HF_PRIMARY_MODEL

class QuoteCalculateRequest(BaseModel):
    selected_items: List[Dict[str, Any]]
    contract_months: int = 12

class CreateOrderRequest(BaseModel):
    business_name: str
    contact_name: str
    contact_phone: str
    city: str
    selected_items: List[Dict[str, Any]]
    contract_months: int = 12
    kyc_applicant_id: Optional[str] = None

class PropensityScoreRequest(BaseModel):
    segment: str
    city_tier: int = 2
    employee_count: int = 3
    num_sites: int = 1
    has_gstin: bool = True
    has_udyam: bool = True
    annual_turnover_band: str = "40 lakh - 1.5 cr"

# ----------------- API Endpoints -----------------

@app.get("/api/health")
def health_check():
    return {"status": "HEALTHY", "track": "Airtel SYNC - Digital Track", "catalogue_products": len(load_catalogue())}

@app.get("/api/catalogue")
def get_catalogue_endpoint():
    return {"products": list(load_catalogue().values())}

@app.get("/api/registry/gstin/{gstin}")
def api_lookup_gstin(gstin: str):
    return lookup_gstin(gstin)

@app.get("/api/registry/udyam/{udyam_number}")
def api_lookup_udyam(udyam_number: str):
    return lookup_udyam(udyam_number)

@app.post("/api/advisor/chat")
def api_advisor_chat(req: AdvisorMessageRequest):
    return generate_advisor_response(
        user_message=req.message,
        conversation_history=req.history,
        hf_token=req.hf_token,
        model_name=req.model_name or HF_PRIMARY_MODEL
    )

@app.get("/api/eligibility")
def api_eligibility(
    city_tier: int = 2,
    employee_count: int = 3,
    num_sites: int = 1,
    has_active_gstin: bool = False,
    segment: Optional[str] = None
):
    return get_eligible_products(city_tier, employee_count, num_sites, has_active_gstin, segment)

@app.post("/api/quote/calculate")
def api_calculate_quote(req: QuoteCalculateRequest):
    return calculate_quote(req.selected_items, req.contract_months)

@app.post("/api/kyc/verify-applicant")
def api_verify_kyc(
    applicant_id: str = Form(...),
    consent_given: bool = Form(True),
    hf_token: Optional[str] = Form(None)
):
    return verify_applicant_kyc(
        applicant_id=applicant_id.strip().upper(),
        consent_given=consent_given,
        hf_token=hf_token
    )

@app.post("/api/orders/create")
def api_create_order(req: CreateOrderRequest):
    return create_digital_order(
        business_name=req.business_name,
        contact_name=req.contact_name,
        contact_phone=req.contact_phone,
        city=req.city,
        selected_items=req.selected_items,
        contract_months=req.contract_months,
        kyc_applicant_id=req.kyc_applicant_id
    )

@app.get("/api/orders/{order_id}")
def api_get_order(order_id: str):
    res = get_order_status(order_id)
    if not res:
        raise HTTPException(status_code=404, detail="Order not found")
    return res

@app.post("/api/propensity/score")
def api_score_lead(req: PropensityScoreRequest):
    return predict_lead_propensity(req.dict())

@app.get("/api/backoffice/unclosed-leads")
def api_unclosed_leads(limit: int = 15):
    return {"unclosed_leads": get_unclosed_leads_queue(limit=limit)}

# ----------------- Frontend UI -----------------
# ponytail: Single-file mobile-first responsive HTML5/Tailwind/Lucide UI eliminates node_modules build friction for judges. Upgrade: Standalone Next.js PWA.

@app.get("/", response_class=HTMLResponse)
def serve_portal():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Airtel Udyam Digital | Go Digital in One Sitting</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0f172a; color: #f8fafc; }
    .airtel-red { background-color: #e11900; }
    .airtel-border { border-color: #e11900; }
    .airtel-text { color: #e11900; }
    .card-glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
  </style>
</head>
<body class="min-h-screen flex flex-col justify-between">

  <!-- Header -->
  <header class="card-glass border-b border-slate-800 sticky top-0 z-50 px-4 py-3">
    <div class="max-w-6xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-red-600 flex items-center justify-center font-bold text-white shadow-lg shadow-red-600/30">
          <i data-lucide="radio" class="w-6 h-6"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-extrabold text-lg text-white tracking-tight">Airtel <span class="text-red-500">SYNC</span></span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 font-semibold">Udyam Digital</span>
          </div>
          <p class="text-[11px] text-slate-400">Making Indian MSMEs go digital in one sitting</p>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <div class="hidden sm:flex items-center space-x-1 text-xs bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="text-slate-300">Free Hugging Face LLM & Vision</span>
        </div>
        <button onclick="switchTab('tracker')" class="text-xs flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700 transition">
          <i data-lucide="package-search" class="w-4 h-4 text-red-400"></i>
          <span>Track Order</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Navigation Tabs -->
  <div class="max-w-6xl mx-auto w-full px-4 pt-4">
    <div class="flex space-x-2 border-b border-slate-800 pb-2 overflow-x-auto">
      <button onclick="switchTab('advisor')" id="tab-btn-advisor" class="tab-btn px-4 py-2 rounded-xl text-sm font-semibold flex items-center space-x-2 bg-red-600 text-white transition">
        <i data-lucide="sparkles" class="w-4 h-4"></i>
        <span>1. AI Advisor</span>
      </button>
      <button onclick="switchTab('quote')" id="tab-btn-quote" class="tab-btn px-4 py-2 rounded-xl text-sm font-semibold flex items-center space-x-2 bg-slate-800/80 text-slate-400 hover:text-white transition">
        <i data-lucide="receipt" class="w-4 h-4"></i>
        <span>2. Transparent Quote</span>
      </button>
      <button onclick="switchTab('kyc')" id="tab-btn-kyc" class="tab-btn px-4 py-2 rounded-xl text-sm font-semibold flex items-center space-x-2 bg-slate-800/80 text-slate-400 hover:text-white transition">
        <i data-lucide="shield-check" class="w-4 h-4"></i>
        <span>3. Smart KYC (DPDP)</span>
      </button>
      <button onclick="switchTab('tracker')" id="tab-btn-tracker" class="tab-btn px-4 py-2 rounded-xl text-sm font-semibold flex items-center space-x-2 bg-slate-800/80 text-slate-400 hover:text-white transition">
        <i data-lucide="clock" class="w-4 h-4"></i>
        <span>4. Order Tracker</span>
      </button>
      <button onclick="switchTab('backoffice')" id="tab-btn-backoffice" class="tab-btn px-4 py-2 rounded-xl text-sm font-semibold flex items-center space-x-2 bg-slate-800/80 text-slate-400 hover:text-white transition">
        <i data-lucide="trending-up" class="w-4 h-4"></i>
        <span>5. Partner Leads Queue</span>
      </button>
    </div>
  </div>

  <!-- Main Content Container -->
  <main class="max-w-6xl mx-auto w-full px-4 py-6 flex-grow">
    
    <!-- ================= TAB 1: ADVISOR ================= -->
    <div id="tab-advisor" class="tab-pane grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Chat Interface -->
      <div class="lg:col-span-2 card-glass rounded-2xl p-4 flex flex-col h-[600px]">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
          <div class="flex items-center space-x-2.5">
            <div class="w-3 h-3 rounded-full bg-emerald-400"></div>
            <span class="text-sm font-semibold text-slate-200">Conversational Needs Advisor</span>
          </div>
          <div class="flex items-center space-x-2">
            <select id="chatLanguage" class="bg-slate-900 text-xs border border-slate-700 rounded-lg px-2.5 py-1 text-slate-300">
              <option value="English">English</option>
              <option value="Hindi">हिंदी (Hindi)</option>
            </select>
            <button onclick="fillPrompt('kirana')" class="text-[11px] bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded-md text-slate-300 border border-slate-700">🏪 Kirana</button>
            <button onclick="fillPrompt('clinic')" class="text-[11px] bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded-md text-slate-300 border border-slate-700">🩺 Clinic</button>
          </div>
        </div>

        <!-- Chat Messages -->
        <div id="chatMessages" class="flex-grow overflow-y-auto space-y-3 pr-2 mb-3">
          <div class="flex items-start space-x-2.5">
            <div class="w-8 h-8 rounded-full bg-red-600/20 text-red-400 flex items-center justify-center shrink-0 border border-red-500/20">
              <i data-lucide="bot" class="w-4 h-4"></i>
            </div>
            <div class="bg-slate-800/80 rounded-2xl rounded-tl-none p-3.5 max-w-[85%] text-sm text-slate-200 border border-slate-700/60 leading-relaxed">
              Hello! I am your <b>Airtel Digital Advisor</b>. Tell me about your business (e.g. clinic in Delhi with 10 staff, or kirana store in Lucknow) and what digital tools you need.
              <br><br><span class="text-xs text-slate-400">आप हिंदी में भी पूछ सकते हैं (जैसे: 'मेरी लखनऊ में दुकान है, WiFi और UPI चाहिए')।</span>
            </div>
          </div>
        </div>

        <!-- Input Box -->
        <form onsubmit="sendChatMessage(event)" class="flex space-x-2 pt-2 border-t border-slate-800">
          <input id="chatInput" type="text" placeholder="Describe your business and needs..." 
                 class="flex-grow bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-red-500 transition">
          <button type="submit" id="sendBtn" class="bg-red-600 hover:bg-red-700 text-white font-semibold px-5 py-2.5 rounded-xl text-sm flex items-center space-x-1 shadow-lg shadow-red-600/20 transition">
            <span>Send</span>
            <i data-lucide="send" class="w-4 h-4"></i>
          </button>
        </form>
      </div>

      <!-- Live Recommendation & Eligibility Card -->
      <div class="card-glass rounded-2xl p-5 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-base text-white flex items-center space-x-2">
              <i data-lucide="package-check" class="w-5 h-5 text-red-500"></i>
              <span>Active Recommendation</span>
            </h3>
            <span id="detectedSegmentBadge" class="text-xs bg-red-500/10 text-red-400 border border-red-500/20 px-2 py-0.5 rounded-full font-medium">Micro Retail</span>
          </div>

          <div id="bundleItemsContainer" class="space-y-2 mb-4">
            <div class="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex justify-between items-center">
              <div>
                <div class="text-sm font-semibold text-slate-200">Biz Fibre 100 (P01)</div>
                <div class="text-xs text-slate-400">100 Mbps Unlimited Broadband</div>
              </div>
              <div class="text-sm font-bold text-slate-100">₹999/mo</div>
            </div>
            <div class="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex justify-between items-center">
              <div>
                <div class="text-sm font-semibold text-slate-200">Secure Wi-Fi + Guest (P22)</div>
                <div class="text-xs text-slate-400">Separate Customer Network</div>
              </div>
              <div class="text-sm font-bold text-slate-100">₹499/mo</div>
            </div>
            <div class="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex justify-between items-center">
              <div>
                <div class="text-sm font-semibold text-slate-200">Business Postpaid 299 (P07)</div>
                <div class="text-xs text-slate-400">50GB Unlimited Calls</div>
              </div>
              <div class="text-sm font-bold text-slate-100">₹349/mo</div>
            </div>
          </div>

          <div class="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
            <div class="flex justify-between text-slate-400">
              <span>Transparent Monthly:</span>
              <span id="recMonthly" class="text-base font-bold text-white">₹1,847/mo</span>
            </div>
            <div class="flex justify-between text-slate-400">
              <span>One-Time Setup:</span>
              <span id="recSetup" class="text-slate-200">₹1,000</span>
            </div>
            <div class="flex justify-between text-slate-400">
              <span>Est. Delivery:</span>
              <span id="recInstall" class="text-emerald-400 font-medium">5 Days (Fibre SLA)</span>
            </div>
          </div>
        </div>

        <button onclick="transferToQuote()" class="w-full mt-4 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-xl text-sm flex items-center justify-center space-x-2 transition shadow-lg shadow-red-600/30">
          <span>Proceed to Quote & Add-ons</span>
          <i data-lucide="arrow-right" class="w-4 h-4"></i>
        </button>
      </div>
    </div>

    <!-- ================= TAB 2: QUOTE & CHECKOUT ================= -->
    <div id="tab-quote" class="tab-pane hidden grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 card-glass rounded-2xl p-6">
        <div class="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
          <div>
            <h2 class="text-lg font-bold text-white">Consolidated SMB Bundle Quote</h2>
            <p class="text-xs text-slate-400">Toggle add-ons with zero hidden fees. Single monthly invoice.</p>
          </div>
          <span class="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-full font-medium">
            15% Consolidator Discount Active
          </span>
        </div>

        <!-- Add-on Toggles -->
        <h3 class="text-sm font-semibold text-slate-300 mb-3">Customizable Products & Add-ons</h3>
        <div id="quoteProductsList" class="space-y-3 mb-6">
          <!-- Dynamically populated -->
        </div>

        <!-- Contract Duration Selector -->
        <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
          <div>
            <div class="text-sm font-semibold text-slate-200">Contract Duration</div>
            <div class="text-xs text-slate-400">24+ month contracts waive all hardware setup fees</div>
          </div>
          <div class="flex space-x-2">
            <button onclick="setContractMonths(12)" id="btn-c-12" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-red-600 text-white">12 Months</button>
            <button onclick="setContractMonths(24)" id="btn-c-24" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400">24 Months (0 Setup)</button>
            <button onclick="setContractMonths(36)" id="btn-c-36" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400">36 Months</button>
          </div>
        </div>
      </div>

      <!-- Checkout Summary Card -->
      <div class="card-glass rounded-2xl p-6 flex flex-col justify-between">
        <div>
          <h3 class="text-base font-bold text-white mb-4">Transparent Pricing Breakdown</h3>
          <div class="space-y-3 text-sm pb-4 border-b border-slate-800">
            <div class="flex justify-between text-slate-400">
              <span>Services Subtotal:</span>
              <span id="sumSubtotal" class="text-slate-200">₹2,847</span>
            </div>
            <div class="flex justify-between text-emerald-400">
              <span>Consolidated Discount:</span>
              <span id="sumDiscount">- ₹285</span>
            </div>
            <div class="flex justify-between text-slate-400">
              <span>GST (18% Statutory):</span>
              <span id="sumGst" class="text-slate-200">₹461</span>
            </div>
            <div class="flex justify-between text-slate-400">
              <span>One-Time Setup Fee:</span>
              <span id="sumSetup" class="text-slate-200">₹1,000</span>
            </div>
            <div class="pt-2 border-t border-slate-800/80 flex justify-between items-baseline">
              <span class="text-base font-bold text-white">Consolidated Monthly:</span>
              <span id="sumTotal" class="text-2xl font-extrabold text-red-500">₹3,023/mo</span>
            </div>
          </div>

          <div class="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs text-emerald-300 flex items-center space-x-2">
            <i data-lucide="sparkles" class="w-4 h-4 shrink-0"></i>
            <span>Estimated <b>₹1,050/mo saved</b> compared to buying from 3 separate local vendors!</span>
          </div>
        </div>

        <button onclick="switchTab('kyc')" class="w-full mt-6 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-xl text-sm flex items-center justify-center space-x-2 transition shadow-lg shadow-red-600/30">
          <span>Accept Quote & Complete KYC</span>
          <i data-lucide="shield-check" class="w-4 h-4"></i>
        </button>
      </div>
    </div>

    <!-- ================= TAB 3: SMART KYC ================= -->
    <div id="tab-kyc" class="tab-pane hidden grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 card-glass rounded-2xl p-6">
        <div class="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
          <div>
            <h2 class="text-lg font-bold text-white">Smart KYC & Verification Engine</h2>
            <p class="text-xs text-slate-400">Instant GSTIN/Udyam lookup with planted trap detection and DPDP Act compliance.</p>
          </div>
          <span class="text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2.5 py-1 rounded-full font-medium">
            DPDP Act 2023 Compliant
          </span>
        </div>

        <!-- Specimen Selector for Judge Testing -->
        <div class="mb-5 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <label class="block text-xs font-semibold text-slate-300 mb-2">Test with Hackathon Specimen Applicants (Planted Traps):</label>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <button onclick="selectKycSpecimen('K01')" id="btn-k-K01" class="kyc-spec-btn p-2 rounded-lg text-xs font-semibold bg-red-600 text-white text-left">
              <div>K01 (Dental)</div>
              <div class="text-[10px] opacity-75">Trap: Missing Udyam</div>
            </button>
            <button onclick="selectKycSpecimen('K02')" id="btn-k-K02" class="kyc-spec-btn p-2 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 text-left">
              <div>K02 (Harmony)</div>
              <div class="text-[10px] opacity-75">Trap: Rotated Doc</div>
            </button>
            <button onclick="selectKycSpecimen('K04')" id="btn-k-K04" class="kyc-spec-btn p-2 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 text-left">
              <div>K04 (Saffron)</div>
              <div class="text-[10px] opacity-75">Trap: Blurry Image</div>
            </button>
            <button onclick="selectKycSpecimen('K05')" id="btn-k-K05" class="kyc-spec-btn p-2 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 text-left">
              <div>K05 (Balaji)</div>
              <div class="text-[10px] opacity-75">Trap: Name Mismatch</div>
            </button>
          </div>
        </div>

        <!-- DPDP Consent Screen -->
        <div class="p-4 rounded-xl bg-blue-950/20 border border-blue-500/30 mb-6">
          <div class="flex items-start space-x-3">
            <input type="checkbox" id="dpdpConsent" checked class="mt-1 rounded border-slate-700 text-red-600 focus:ring-red-500">
            <div class="text-xs text-slate-300 leading-relaxed">
              <span class="font-bold text-white">DPDP Act 2023 Explicit Consent:</span> I hereby consent to Accel Business verifying my GSTIN and Udyam credentials solely for enterprise broadband provisioning. Documents are encrypted and retained for 30 days max. All PII is masked in logs.
            </div>
          </div>
        </div>

        <!-- Run Verification Button -->
        <button onclick="runKycVerification()" id="verifyKycBtn" class="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-xl text-sm flex items-center justify-center space-x-2 transition shadow-lg shadow-red-600/30">
          <i data-lucide="scan-face" class="w-4 h-4"></i>
          <span>Run Instant Smart KYC Verification</span>
        </button>
      </div>

      <!-- KYC Result Card -->
      <div class="card-glass rounded-2xl p-6 flex flex-col justify-between">
        <div>
          <h3 class="text-base font-bold text-white mb-4">Verification Findings</h3>
          <div id="kycResultContainer" class="space-y-3">
            <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center text-xs text-slate-400">
              Click 'Run Instant Smart KYC Verification' to analyze documents against mock registries and validation rules.
            </div>
          </div>
        </div>

        <button onclick="completeOrderAndTrack()" id="orderConfirmBtn" disabled class="w-full mt-6 bg-slate-800 text-slate-500 font-semibold py-3 rounded-xl text-sm flex items-center justify-center space-x-2 transition cursor-not-allowed">
          <span>Place Digital Order</span>
          <i data-lucide="check-circle" class="w-4 h-4"></i>
        </button>
      </div>
    </div>

    <!-- ================= TAB 4: ORDER TRACKER ================= -->
    <div id="tab-tracker" class="tab-pane hidden max-w-3xl mx-auto card-glass rounded-2xl p-6">
      <div class="flex items-center justify-between pb-4 mb-6 border-b border-slate-800">
        <div>
          <span class="text-xs font-semibold text-red-400 uppercase tracking-wider">Live Order Status</span>
          <h2 id="trackerOrderId" class="text-xl font-extrabold text-white">ORD-261107-LIVE</h2>
          <p id="trackerBusinessName" class="text-xs text-slate-400">Balaji Dental Care LLP · Tier 2 (Kochi)</p>
        </div>
        <div class="text-right">
          <div class="text-xs text-slate-400">Est. Live Go-Live</div>
          <div id="trackerGoLiveDate" class="text-base font-bold text-emerald-400">July 20, 2026</div>
        </div>
      </div>

      <!-- Milestones Timeline -->
      <div id="milestonesContainer" class="space-y-6 relative pl-6 before:content-[''] before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
        <!-- Dynamically populated -->
      </div>
    </div>

    <!-- ================= TAB 5: PARTNER BACK-OFFICE ================= -->
    <div id="tab-backoffice" class="tab-pane hidden card-glass rounded-2xl p-6">
      <div class="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
        <div>
          <h2 class="text-lg font-bold text-white">Partner & Field Sales Recovery Queue</h2>
          <p class="text-xs text-slate-400">Unclosed leads from the digital advisor scored by ML conversion propensity.</p>
        </div>
        <div class="text-xs bg-red-500/10 text-red-400 border border-red-500/20 px-3 py-1 rounded-full font-semibold">
          Scikit-Learn Logistic Regression (ROC-AUC: 0.69)
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead>
            <tr class="text-slate-400 border-b border-slate-800">
              <th class="py-2.5 px-3">Lead ID</th>
              <th class="py-2.5 px-3">Business</th>
              <th class="py-2.5 px-3">Segment</th>
              <th class="py-2.5 px-3">Stage Dropped</th>
              <th class="py-2.5 px-3">Drop Reason</th>
              <th class="py-2.5 px-3">Propensity</th>
              <th class="py-2.5 px-3">Recommended Action</th>
            </tr>
          </thead>
          <tbody id="unclosedLeadsTable" class="divide-y divide-slate-800/60 text-slate-300">
            <!-- Dynamically populated -->
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <!-- Footer -->
  <footer class="card-glass border-t border-slate-800 px-4 py-3 text-center text-xs text-slate-500">
    Airtel SYNC · Track A Enterprise: Project Udyam Digital · Fully Compliant with DPDP Act, 2023
  </footer>

  <script>
    // State
    let currentTab = 'advisor';
    let selectedKycApplicant = 'K01';
    let contractMonths = 12;
    let selectedProducts = [
      { product_id: 'P01', quantity: 1 },
      { product_id: 'P22', quantity: 1 },
      { product_id: 'P07', quantity: 1 }
    ];
    let allCatalogue = [];

    // Switch Tabs
    function switchTab(tabId) {
      document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('bg-red-600', 'text-white');
        btn.classList.add('bg-slate-800/80', 'text-slate-400');
      });

      document.getElementById('tab-' + tabId).classList.remove('hidden');
      const activeBtn = document.getElementById('tab-btn-' + tabId);
      if (activeBtn) {
        activeBtn.classList.remove('bg-slate-800/80', 'text-slate-400');
        activeBtn.classList.add('bg-red-600', 'text-white');
      }
      currentTab = tabId;

      if (tabId === 'quote') loadQuotePage();
      if (tabId === 'backoffice') loadBackofficeLeads();
      lucide.createIcons();
    }

    // Quick Prompts
    function fillPrompt(type) {
      const input = document.getElementById('chatInput');
      if (type === 'kirana') {
        input.value = "नमस्ते! मेरी लखनऊ में 2 लोगों की किराना दुकान है। मुझे UPI पेमेंट के लिए अच्छा इंटरनेट और ग्राहकों के लिए WhatsApp चाहिए।";
      } else {
        input.value = "We run a dental clinic in Mumbai with 12 staff. We have GST. Need reliable broadband, staff emails and CCTV backup.";
      }
    }

    // Chat handling
    async function sendChatMessage(e) {
      e.preventDefault();
      const input = document.getElementById('chatInput');
      const text = input.value.trim();
      if (!text) return;

      appendMessage('user', text);
      input.value = '';

      const sendBtn = document.getElementById('sendBtn');
      sendBtn.disabled = true;
      sendBtn.innerHTML = '<span>Thinking...</span>';

      try {
        const res = await fetch('/api/advisor/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, history: [] })
        });
        const data = await res.json();
        appendMessage('bot', data.text);

        // Update recommendation card
        if (data.bundle && data.bundle.bundle_items) {
          updateRecommendationCard(data);
        }
      } catch (err) {
        appendMessage('bot', 'Sorry, I encountered an error connecting to the advisor service.');
      } finally {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<span>Send</span><i data-lucide="send" class="w-4 h-4"></i>';
        lucide.createIcons();
      }
    }

    function appendMessage(sender, text) {
      const container = document.getElementById('chatMessages');
      const isUser = sender === 'user';
      const div = document.createElement('div');
      div.className = isUser ? 'flex justify-end' : 'flex items-start space-x-2.5';

      div.innerHTML = isUser ? 
        `<div class="bg-red-600 rounded-2xl rounded-tr-none p-3.5 max-w-[85%] text-sm text-white shadow-md leading-relaxed">${text}</div>` :
        `<div class="w-8 h-8 rounded-full bg-red-600/20 text-red-400 flex items-center justify-center shrink-0 border border-red-500/20">
          <i data-lucide="bot" class="w-4 h-4"></i>
        </div>
        <div class="bg-slate-800/80 rounded-2xl rounded-tl-none p-3.5 max-w-[85%] text-sm text-slate-200 border border-slate-700/60 leading-relaxed whitespace-pre-line">${text}</div>`;

      container.appendChild(div);
      container.scrollTop = container.scrollHeight;
      lucide.createIcons();
    }

    function updateRecommendationCard(data) {
      document.getElementById('detectedSegmentBadge').innerText = data.profile.segment;
      document.getElementById('recMonthly').innerText = '₹' + data.bundle.summary.monthly_recommended.toLocaleString() + '/mo';
      document.getElementById('recSetup').innerText = '₹' + data.bundle.summary.one_time_setup.toLocaleString();
      document.getElementById('recInstall').innerText = data.bundle.summary.estimated_delivery_days + ' Days';

      const itemsContainer = document.getElementById('bundleItemsContainer');
      itemsContainer.innerHTML = '';
      selectedProducts = [];

      data.bundle.bundle_items.forEach(item => {
        selectedProducts.push({ product_id: item.product_id, quantity: item.quantity });
        const pdiv = document.createElement('div');
        pdiv.className = 'p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex justify-between items-center';
        pdiv.innerHTML = `
          <div>
            <div class="text-sm font-semibold text-slate-200">${item.product_name}</div>
            <div class="text-xs text-slate-400">Qty: ${item.quantity} · ${item.unit}</div>
          </div>
          <div class="text-sm font-bold text-slate-100">₹${item.monthly_price_min}</div>
        `;
        itemsContainer.appendChild(pdiv);
      });
    }

    function transferToQuote() {
      switchTab('quote');
    }

    // Quote Page
    async function loadQuotePage() {
      if (allCatalogue.length === 0) {
        const catRes = await fetch('/api/catalogue');
        const catData = await catRes.json();
        allCatalogue = catData.products;
      }

      const container = document.getElementById('quoteProductsList');
      container.innerHTML = '';

      allCatalogue.forEach(prod => {
        const isSelected = selectedProducts.some(p => p.product_id === prod.product_id);
        const card = document.createElement('div');
        card.className = `p-3 rounded-xl border flex items-center justify-between transition ${isSelected ? 'bg-slate-800/90 border-red-500/50' : 'bg-slate-900/50 border-slate-800'}`;
        card.innerHTML = `
          <div class="flex items-center space-x-3">
            <input type="checkbox" onchange="toggleProduct('${prod.product_id}', this.checked)" ${isSelected ? 'checked' : ''} class="w-4 h-4 rounded text-red-600 focus:ring-red-500">
            <div>
              <div class="text-sm font-semibold text-slate-200">${prod.product_name} <span class="text-xs text-slate-400">(${prod.product_id})</span></div>
              <div class="text-xs text-slate-400">${prod.description}</div>
            </div>
          </div>
          <div class="text-right">
            <div class="text-sm font-bold text-slate-200">₹${Math.round((prod.price_min + prod.price_max)/2)}/mo</div>
            <div class="text-[11px] text-slate-400">${prod.unit}</div>
          </div>
        `;
        container.appendChild(card);
      });

      refreshQuotePricing();
    }

    function toggleProduct(pid, checked) {
      if (checked) {
        selectedProducts.push({ product_id: pid, quantity: 1 });
      } else {
        selectedProducts = selectedProducts.filter(p => p.product_id !== pid);
      }
      loadQuotePage();
    }

    function setContractMonths(m) {
      contractMonths = m;
      document.querySelectorAll('[id^="btn-c-"]').forEach(b => {
        b.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400';
      });
      document.getElementById('btn-c-' + m).className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-red-600 text-white';
      refreshQuotePricing();
    }

    async function refreshQuotePricing() {
      const res = await fetch('/api/quote/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selected_items: selectedProducts, contract_months: contractMonths })
      });
      const data = await res.json();
      const p = data.pricing_summary;

      document.getElementById('sumSubtotal').innerText = '₹' + p.monthly_subtotal.toLocaleString();
      document.getElementById('sumDiscount').innerText = '- ₹' + p.bundle_discount_inr.toLocaleString();
      document.getElementById('sumGst').innerText = '₹' + p.gst_18_pct.toLocaleString();
      document.getElementById('sumSetup').innerText = p.setup_discount_applied ? 'Waived (Free)' : '₹' + p.one_time_setup_fee_inr.toLocaleString();
      document.getElementById('sumTotal').innerText = '₹' + p.total_monthly_bill_inr.toLocaleString() + '/mo';
    }

    // KYC Page
    function selectKycSpecimen(kId) {
      selectedKycApplicant = kId;
      document.querySelectorAll('.kyc-spec-btn').forEach(b => {
        b.className = 'kyc-spec-btn p-2 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 text-left';
      });
      document.getElementById('btn-k-' + kId).className = 'kyc-spec-btn p-2 rounded-lg text-xs font-semibold bg-red-600 text-white text-left';
    }

    async function runKycVerification() {
      const consent = document.getElementById('dpdpConsent').checked;
      const btn = document.getElementById('verifyKycBtn');
      btn.disabled = true;
      btn.innerText = 'Verifying with Hugging Face Vision & Registries...';

      const formData = new FormData();
      formData.append('applicant_id', selectedKycApplicant);
      formData.append('consent_given', consent);

      try {
        const res = await fetch('/api/kyc/verify-applicant', { method: 'POST', body: formData });
        const data = await res.json();
        renderKycResults(data);
      } catch (e) {
        alert('Error performing KYC verification');
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="scan-face" class="w-4 h-4"></i><span>Run Instant Smart KYC Verification</span>';
        lucide.createIcons();
      }
    }

    function renderKycResults(data) {
      const container = document.getElementById('kycResultContainer');
      const confirmBtn = document.getElementById('orderConfirmBtn');

      let statusBadge = data.passed ? 
        `<span class="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs flex items-center space-x-1.5"><i data-lucide="check-circle" class="w-4 h-4"></i><span>APPROVED (Instant Digital KYC)</span></span>` :
        `<span class="px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 font-bold text-xs flex items-center space-x-1.5"><i data-lucide="alert-triangle" class="w-4 h-4"></i><span>ACTION REQUIRED</span></span>`;

      let errorsHtml = '';
      if (data.fatal_errors && data.fatal_errors.length > 0) {
        errorsHtml = '<div class="space-y-1.5">' + data.fatal_errors.map(err => 
          `<div class="text-xs p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-start space-x-2"><i data-lucide="x-circle" class="w-4 h-4 text-rose-400 shrink-0 mt-0.5"></i><span>${err}</span></div>`
        ).join('') + '</div>';
      }

      let warningsHtml = '';
      if (data.warnings && data.warnings.length > 0) {
        warningsHtml = '<div class="space-y-1.5">' + data.warnings.map(w => 
          `<div class="text-xs p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 flex items-start space-x-2"><i data-lucide="alert-circle" class="w-4 h-4 text-amber-400 shrink-0 mt-0.5"></i><span>${w}</span></div>`
        ).join('') + '</div>';
      }

      container.innerHTML = `
        <div class="pb-3 border-b border-slate-800 flex justify-between items-center">
          <span class="text-xs text-slate-400 font-semibold">Applicant: ${data.applicant_id}</span>
          ${statusBadge}
        </div>
        ${errorsHtml}
        ${warningsHtml}
        <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 text-xs space-y-1.5">
          <div class="text-slate-400 font-semibold mb-1">Masked Registry Matches (DPDP Act):</div>
          <div class="flex justify-between"><span class="text-slate-500">GSTIN:</span><span class="text-slate-200 font-mono">${data.masked_summary.gstin || 'None'}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Registry Status:</span><span class="text-slate-200">${data.masked_summary.gstin_registry_status || 'Unverified'}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Udyam No:</span><span class="text-slate-200 font-mono">${data.masked_summary.udyam_number}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Electricity Billed:</span><span class="text-slate-200">${data.masked_summary.consumer_no || 'Verified'}</span></div>
        </div>
      `;

      if (data.passed) {
        confirmBtn.disabled = false;
        confirmBtn.className = 'w-full mt-6 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-3 rounded-xl text-sm flex items-center justify-center space-x-2 transition cursor-pointer shadow-lg shadow-emerald-600/30';
      } else {
        confirmBtn.disabled = true;
        confirmBtn.className = 'w-full mt-6 bg-slate-800 text-slate-500 font-semibold py-3 rounded-xl text-sm flex items-center justify-center space-x-2 transition cursor-not-allowed';
      }
      lucide.createIcons();
    }

    async function completeOrderAndTrack() {
      const orderPayload = {
        business_name: selectedKycApplicant === 'K02' ? 'Harmony Dental Care' : 'Balaji Dental Care LLP',
        contact_name: 'Dr. Joseph Shah',
        contact_phone: '+91 98765 43210',
        city: 'Kolkata',
        selected_items: selectedProducts,
        contract_months: contractMonths,
        kyc_applicant_id: selectedKycApplicant
      };

      const res = await fetch('/api/orders/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderPayload)
      });
      const order = await res.json();
      displayOrderTracking(order);
      switchTab('tracker');
    }

    function displayOrderTracking(order) {
      document.getElementById('trackerOrderId').innerText = order.order_id;
      document.getElementById('trackerBusinessName').innerText = `${order.business_name} · ${order.city}`;
      document.getElementById('trackerGoLiveDate').innerText = order.expected_activation_date;

      const container = document.getElementById('milestonesContainer');
      container.innerHTML = '';

      order.milestones.forEach((m, idx) => {
        const isDone = m.status === 'COMPLETED';
        const isProgress = m.status === 'IN_PROGRESS';
        const iconBg = isDone ? 'bg-emerald-500 text-white' : (isProgress ? 'bg-red-600 text-white animate-pulse' : 'bg-slate-800 text-slate-500');
        const icon = isDone ? 'check' : (isProgress ? 'loader-2' : 'clock');

        const div = document.createElement('div');
        div.className = 'relative flex items-start space-x-3';
        div.innerHTML = `
          <div class="w-6 h-6 rounded-full ${iconBg} flex items-center justify-center shrink-0 text-xs shadow-md z-10 -ml-[19px]">
            <i data-lucide="${icon}" class="w-3.5 h-3.5"></i>
          </div>
          <div class="flex-grow">
            <div class="flex justify-between items-baseline">
              <span class="text-sm font-semibold text-white">${m.title}</span>
              <span class="text-xs text-slate-400 font-mono">${m.date}</span>
            </div>
            <p class="text-xs text-slate-400 mt-0.5">${m.desc}</p>
          </div>
        `;
        container.appendChild(div);
      });
      lucide.createIcons();
    }

    // Backoffice leads queue
    async function loadBackofficeLeads() {
      const res = await fetch('/api/backoffice/unclosed-leads?limit=10');
      const data = await res.json();
      const tbody = document.getElementById('unclosedLeadsTable');
      tbody.innerHTML = '';

      data.unclosed_leads.forEach(l => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition';
        tr.innerHTML = `
          <td class="py-2.5 px-3 font-mono text-slate-400">${l.lead_id}</td>
          <td class="py-2.5 px-3 font-semibold text-white">${l.business_name}</td>
          <td class="py-2.5 px-3 text-slate-400">${l.segment}</td>
          <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded-full bg-slate-800 text-[10px]">${l.stage_reached}</span></td>
          <td class="py-2.5 px-3 text-rose-400">${l.drop_reason}</td>
          <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 font-bold font-mono">${l.propensity_score}%</span></td>
          <td class="py-2.5 px-3 text-[11px] text-amber-300 font-medium">${l.recommended_sales_hook}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    // Initialize icons
    window.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
    });
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

