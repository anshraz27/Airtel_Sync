import os
from reportlab.pdfgen import canvas
from reportlab.lib import colors

OUT_DIR = r"c:\Users\thean\Desktop\airtel_digital"
PDF_PATH = os.path.join(OUT_DIR, "Airtel_SYNC_Udyam_Digital_7Slides.pdf")

# Palette
RED = colors.HexColor("#E51B00")
DARK = colors.HexColor("#0F172A")
SLATE = colors.HexColor("#1E293B")
CARD_BORDER = colors.HexColor("#334155")
WHITE = colors.HexColor("#FFFFFF")
LIGHT = colors.HexColor("#F1F5F9")
MUTED = colors.HexColor("#94A3B8")
GREEN = colors.HexColor("#10B981")
AMBER = colors.HexColor("#F59E0B")
BLUE = colors.HexColor("#38BDF8")
TRACK = colors.HexColor("#2D3B50")

W = 960
H = 540

def draw_header(c, title, subtitle, page_num):
    # Left red accent bar
    c.setFillColor(RED)
    c.rect(0, 0, 10, H, fill=1, stroke=0)
    
    # Title & Subtitle
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(24, H - 32, title)
    
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(24, H - 48, subtitle)
    
    # Top right repo badge
    c.setFillColor(SLATE)
    c.roundRect(W - 370, H - 42, 350, 24, 6, fill=1, stroke=1)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(W - 360, H - 32, "Code Repo:")
    c.setFillColor(LIGHT)
    c.setFont("Helvetica", 9)
    c.drawString(W - 295, H - 32, "https://github.com/anshraz27/Airtel_Sync")
    
    # Footer
    c.setStrokeColor(SLATE)
    c.setLineWidth(1)
    c.line(20, 26, W - 20, 26)
    
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(24, 14, "Airtel SYNC · Enterprise Track A (Project Udyam Digital) · Code: https://github.com/anshraz27/Airtel_Sync")
    c.drawRightString(W - 24, 14, f"Slide {page_num} of 7")

def draw_card(c, x, y, w, h, bg=SLATE, border=CARD_BORDER, radius=6):
    c.setFillColor(bg)
    c.setStrokeColor(border)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)

def generate_pdf():
    c = canvas.Canvas(PDF_PATH, pagesize=(W, H))
    
    # ==================== SLIDE 1 ====================
    # Background
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    
    # Red top hero banner
    c.setFillColor(RED)
    c.rect(0, H - 120, W, 120, fill=1, stroke=0)
    
    c.setFillColor(colors.HexColor("#FFCCD0"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(35, H - 28, "YTL HACKATHON 2026 · ENTERPRISE TRACK A")
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(35, H - 64, "Project Udyam Digital")
    
    c.setFillColor(colors.HexColor("#FFE4E6"))
    c.setFont("Helvetica", 14)
    c.drawString(35, H - 88, "Making 6 Crore+ Indian MSMEs Go Digital in One Sitting")
    
    # GitHub Pill on banner
    c.setFillColor(DARK)
    c.roundRect(W - 420, H - 75, 385, 30, 8, fill=1, stroke=0)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(W - 405, H - 62, "GitHub Repo:")
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 10)
    c.drawString(W - 325, H - 62, "https://github.com/anshraz27/Airtel_Sync")
    
    # 4 Pillar cards
    pillars = [
        ("AI Advisor", "Conversational needs discovery\nin Hindi & English via Free HF LLM", "🤖"),
        ("Quote & Checkout", "Single transparent monthly bill,\nzero hidden charges, add-on toggling", "📋"),
        ("Smart KYC", "Instant GSTIN/Udyam lookup,\nLLM Vision OCR & DPDP Act consent", "🛡️"),
        ("Order Tracker", "Milestone activation tracker,\nzero status-chasing calls", "📦")
    ]
    card_w = 215
    for i, (title, desc, icon) in enumerate(pillars):
        cx = 35 + i * (card_w + 20)
        draw_card(c, cx, H - 285, card_w, 145, bg=SLATE, border=RED)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(cx + 15, H - 170, f"{icon} {title}")
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 10)
        for line_idx, line in enumerate(desc.split("\n")):
            c.drawString(cx + 15, H - 200 - line_idx * 16, line)
            
    # Problem Bar (smb_leads.csv data)
    draw_card(c, 35, 45, W - 70, 160, bg=SLATE, border=CARD_BORDER)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 180, "The Core Problem at a Glance (Source: smb_leads.csv · 5,000 SMB Leads, Apr–Jun 2026)")
    
    metrics = [
        ("7.4%", "Lead-to-Activation Rate\n(Only 368/5,000 convert)"),
        ("17.6 Days", "Average Onboarding Cycle\n(Slow, paper-heavy visits)"),
        ("₹15,000", "Blended Acquisition Cost\n(High field sales friction)"),
        ("3 Calls", "Status Chases / Customer\n(Support opaque order trail)"),
        ("4.7x Gap", "GSTIN (9.6%) vs No-GSTIN (2.0%)\n(Severe document dropout)")
    ]
    stat_w = 165
    for i, (val, label) in enumerate(metrics):
        sx = 50 + i * (stat_w + 15)
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(sx, 140, val)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        for line_idx, line in enumerate(label.split("\n")):
            c.drawString(sx, 115 - line_idx * 14, line)
            
    c.showPage()
    
    # ==================== SLIDE 2 ====================
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    draw_header(c, "Slide 2: Target Segments & Prioritisation", "Key Question 1 (Case PDF p.3) · Data Source: smb_leads.csv & Appendix A2", 2)
    
    segs = [
        ("Micro Retail & Services", "55% Base", "Kirana, salon, pharmacy", "Owner mobile + hotspot, UPI QR", "Reliable UPI WiFi, WhatsApp catalogue, single bill", "P01 + P22 + P07 ≈ ₹1,947/mo", "TIER 1 (Volume)", AMBER),
        ("Professional Offices", "25% Base", "Clinic, CA firm, coaching", "Home broadband, personal Gmail", "99.9% uptime, cloud email, security, 4G failover", "P02 + P16 + P20 + P09 ≈ ₹4,813/mo", "TIER 2 (High ARPU)", GREEN),
        ("Small Multi-Site", "15% Base", "Restaurant chain, 3-10 stores", "Mixed local ISPs, no central IT", "Single bill, SD-WAN, cloud CCTV, multi-site SLA", "P02 + P10 + P23 + P09 ≈ ₹7,200/mo", "TIER 3 (High LTV)", BLUE),
        ("Small Manufacturers", "5% Base", "Auto parts, textile units", "Leased line or unmanaged ISP", "Dedicated ILL bandwidth, IoT sensor uptime", "P05/P06 + P24 + P20 ≈ ₹12,000/mo", "TIER 4 (Specialist)", RED)
    ]
    sw = 210
    for i, (title, share, ex, curr, needs, bundle, tier, tcolor) in enumerate(segs):
        sx = 25 + i * (sw + 16)
        draw_card(c, sx, 45, sw, 435, bg=SLATE, border=tcolor)
        
        # Priority Pill
        c.setFillColor(tcolor)
        c.roundRect(sx + 10, 445, sw - 20, 22, 4, fill=1, stroke=0)
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(sx + sw/2, 452, tier)
        
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(sx + 12, 420, title)
        
        c.setFillColor(tcolor)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(sx + 12, 400, f"Share: {share}")
        
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(sx + 12, 380, f"e.g. {ex}")
        
        c.setFillColor(LIGHT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(sx + 12, 350, "Current Setup:")
        c.setFont("Helvetica", 8.5)
        c.setFillColor(MUTED)
        c.drawString(sx + 12, 335, curr[:32])
        c.drawString(sx + 12, 322, curr[32:64])
        
        c.setFillColor(LIGHT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(sx + 12, 290, "Key Digital Needs:")
        c.setFont("Helvetica", 8.5)
        c.setFillColor(MUTED)
        c.drawString(sx + 12, 275, needs[:30])
        c.drawString(sx + 12, 262, needs[30:60])
        
        c.setFillColor(LIGHT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(sx + 12, 230, "Curated Bundle:")
        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(GREEN)
        c.drawString(sx + 12, 215, bundle[:30])
        c.drawString(sx + 12, 202, bundle[30:60])
        
        c.setFillColor(DARK)
        c.roundRect(sx + 10, 60, sw - 20, 40, 4, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(sx + sw/2, 85, "Price Sensitivity:")
        c.setFillColor(tcolor)
        c.drawCentredString(sx + sw/2, 70, "Very High" if i==0 else ("Medium" if i==1 else ("Low-Med" if i==2 else "Low")))

    c.showPage()
    
    # ==================== SLIDE 3 ====================
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    draw_header(c, "Slide 3: Solution Architecture & Engineering Stack", "Submission Requirement 2 (Case PDF p.4) · Multi-layer, Airtel-Scale Architecture", 3)
    
    # Left column: Architecture Layers
    layers = [
        ("Mobile-First Web App (PWA)", "Tailwind + Responsive UI · English & Devanagari Hindi · Zero App Store friction", BLUE),
        ("FastAPI Gateway Layer", "Async REST Gateway · Route auth · PII Masking Middleware · Audit logging", GREEN),
        ("Orchestration & Business Logic", "LangGraph / Deterministic Tool Runner · Quote Math · Milestone Scheduler", AMBER),
        ("Free Hugging Face AI Stack", "Qwen2.5-72B (Advisor) · Qwen2-VL-7B (Vision OCR) · Deterministic Fallback Engine", RED),
        ("Data & Registry Verification", "Mock GSTIN (3,534 recs) · Mock Udyam (2,723 recs) · Mod-36 Checksum · SQLite", MUTED),
        ("Security & DPDP Compliance", "Pre-KYC Consent Gate · Ephemeral Enclave · 30-Day Auto Retention Shredding", BLUE)
    ]
    lh = 55
    for i, (ltitle, ldesc, lcolor) in enumerate(layers):
        ly = H - 120 - i * (lh + 12)
        draw_card(c, 25, ly, 380, lh, bg=SLATE, border=lcolor)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(38, ly + 34, ltitle)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8.5)
        c.drawString(38, ly + 16, ldesc)
        
    # Right column: Component Responsibilities & Code Traceability
    draw_card(c, 420, 45, 515, 435, bg=SLATE, border=CARD_BORDER)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(438, 450, "Component Responsibilities & Repository Traceability")
    
    comps = [
        ("Deterministic Eligibility Engine", "app/eligibility.py", "Enforces city tiers, employee bounds, sites, active GSTIN, and dependency chains in pure Python. Zero LLM hallucination risk."),
        ("Free Hugging Face AI Advisor", "app/advisor.py", "Orchestrates multi-turn conversation via Qwen2.5-72B; features offline fallback engine for 100% demo resilience even with no API key."),
        ("Smart KYC & Anomaly Pipeline", "app/kyc.py", "Qwen2-VL-7B OCR + Laplacian edge variance blur detection + Mod-36 GSTIN checksum + cross-document entity name matcher."),
        ("Transparent Quote Builder", "app/quote.py", "Dynamic add-on toggling, multi-product consolidation discount (10-15%), 18% GST statutory tax, and 24-month contract setup waiver."),
        ("Order Provisioning & Tracker", "app/orders.py", "Generates order IDs and computes activation milestones using product typical_install_days SLA. Eliminates 3x status calls."),
        ("ML Propensity Scoring Model", "app/propensity.py", "Scikit-Learn Logistic Regression on 5,000 leads (ROC-AUC 0.69); feeds Warm Lead Queue to field partners to salvage dropped leads.")
    ]
    for i, (cname, cpath, cdesc) in enumerate(comps):
        cy = 405 - i * 62
        c.setFillColor(AMBER)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(438, cy + 16, cname)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(915, cy + 16, cpath)
        c.setFillColor(LIGHT)
        c.setFont("Helvetica", 8.5)
        c.drawString(438, cy - 2, cdesc[:85])
        c.drawString(438, cy - 14, cdesc[85:170])
        
    c.showPage()
    
    # ==================== SLIDE 4 ====================
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    draw_header(c, "Slide 4: Smart KYC Pipeline & Planted Trap Defences", "Build Challenge (Case PDF p.3) · Key Question 3 · DPDP Act 2023 Compliance", 4)
    
    # Verification Stages
    vsteps = [
        ("1. DPDP Consent", "Explicit checkbox;\npurpose bound to broadband", BLUE),
        ("2. HF Vision OCR", "Qwen2-VL-7B;\nextracts structured JSON", RED),
        ("3. Mod-36 Checksum", "15-char validator;\naccepts PAN 'X' entity", AMBER),
        ("4. Registry Query", "Active/Cancelled/Suspended\nstatus validation", GREEN),
        ("5. Cross-Check", "Name match across docs;\n90-day bill freshness", BLUE),
        ("6. Decision Engine", "Approved or granular\nactionable error notice", GREEN)
    ]
    vw = 140
    for i, (stitle, sdesc, scolor) in enumerate(vsteps):
        vx = 25 + i * (vw + 14)
        draw_card(c, vx, H - 150, vw, 75, bg=SLATE, border=scolor)
        c.setFillColor(scolor)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(vx + 8, H - 95, stitle)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        for line_idx, line in enumerate(sdesc.split("\n")):
            c.drawString(vx + 8, H - 115 - line_idx * 12, line)
            
    # Planted Traps Section
    draw_card(c, 25, 45, W - 50, 315, bg=SLATE, border=RED)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(45, 330, "Specimen Document Planted Trap Analysis (K01–K12 Evaluation Answer Key)")
    
    traps = [
        ("K01 (Balaji Dental / Vindhya)", "Blank Udyam Number + Cancelled GSTIN", "udyam_certificate has empty registration field; GSTIN 37IHKXV5167L1ZS is Cancelled in mock registry.", "FLAGGED: 'Missing Udyam Number' and 'GSTIN is Cancelled (Only Active GSTINs allowed)'", RED),
        ("K02 (Harmony Dental)", "Skewed / Rotated Document Canvas", "Canvas size is 1446x1894 with rotated scan angle exceeding standard A4 ratio.", "RESOLVED: Auto-orientation angle correction applied; OCR extracts valid fields.", AMBER),
        ("K04 (Saffron Dental)", "Blurry / Low-Resolution Document", "Edge-variance Laplacian sharpness score is 175.8 (well below 300 quality threshold).", "REJECTED: Prompted with 'Document blurry (score 175.8), please re-upload clear copy'", RED),
        ("K05 (Balaji Realty)", "Cross-Document Name Mismatch", "GST Certificate trade name is 'Balaji Dental Care LLP' but Electricity Bill is billed to 'Balaji Realty LLP'.", "FLAGGED: 'Entity Name Mismatch between GST Certificate and Address Proof'", RED),
        ("K05 (Balaji Realty)", "Missing Udyam Certificate", "Folder contains only 3 specimen documents; Udyam registration certificate absent.", "WARNED: 'Udyam Certificate not provided; MSME priority benefits cannot be unlocked'", AMBER),
        ("All Applicants", "Address Proof Freshness Gate (<= 90 Days)", "Reference Date set to 2026-07-15 per hackathon rules. Any bill older than 90 days rejected.", "ENFORCED: Real-time date difference calculation prevents expired KYC document fraud.", GREEN)
    ]
    for i, (app, issue, detail, outcome, ocolor) in enumerate(traps):
        ty = 295 - i * 42
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(45, ty + 10, app)
        c.setFillColor(ocolor)
        c.drawString(225, ty + 10, f"Trap: {issue}")
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(45, ty - 4, detail[:95])
        c.setFillColor(GREEN if ocolor==GREEN else (AMBER if ocolor==AMBER else colors.HexColor("#FDA4AF")))
        c.drawString(45, ty - 16, f"Outcome: {outcome}")
        
    c.showPage()
    
    # ==================== SLIDE 5 ====================
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    draw_header(c, "Slide 5: GenAI Advisor & Transparent Quote Builder", "Build Challenge (Case PDF p.3) · Key Question 2 · Plain Language Needs Discovery", 5)
    
    # Left Box: AI Advisor
    draw_card(c, 25, 45, 435, 435, bg=SLATE, border=BLUE)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(45, 450, "🤖 Conversational AI Advisor (Free HF LLM)")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(45, 432, "Hugging Face Serverless Inference API · Qwen2.5-72B-Instruct")
    
    adv_points = [
        ("Free Hugging Face Stack:", "Primary: Qwen/Qwen2.5-72B-Instruct. HF Alternatives: DeepSeek-R1-Distill-Qwen-32B, Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3."),
        ("Multilingual Vernacular:", "Fluidly handles English and Devanagari Hindi (e.g. 'मेरी लखनऊ में किराना दुकान है, WiFi और UPI चाहिए')."),
        ("Zero-Hallucination Guard:", "Eligibility checked in deterministic Python code before LLM synthesizes recommendations. LLM cannot invent invalid bundles."),
        ("100% Offline Demo Resilience:", "Built-in rule-based fallback advisor fires if HF token is missing or network rate-limited. Guaranteeing flawless demo uptime.")
    ]
    for i, (h, p) in enumerate(adv_points):
        py = 390 - i * 65
        c.setFillColor(AMBER)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(45, py + 12, h)
        c.setFillColor(LIGHT)
        c.setFont("Helvetica", 8.5)
        c.drawString(45, py - 2, p[:65])
        c.drawString(45, py - 14, p[65:130])
        c.drawString(45, py - 26, p[130:195])
        
    # Sample chat bubble
    c.setFillColor(colors.HexColor("#1E3A8A"))
    c.roundRect(45, 60, 395, 45, 6, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(55, 88, "User (Kirana Owner):")
    c.setFont("Helvetica", 8)
    c.drawString(55, 72, "नमस्ते! मुझे लखनऊ में 2 लोगों की दुकान के लिए UPI और WiFi चाहिए।")
    
    # Right Box: Quote Builder
    draw_card(c, 480, 45, 455, 435, bg=SLATE, border=GREEN)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(500, 450, "📋 Transparent Quote Builder")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(500, 432, "Directly attacks the #1 funnel killer: 44% quote-stage drop")
    
    q_items = [
        ("Biz Fibre 100 (P01)", "100 Mbps Unlimited Broadband", "₹999/mo"),
        ("Secure Wi-Fi + Guest (P22)", "Separate customer network", "₹499/mo"),
        ("Business Postpaid 299 (P07)", "50 GB Data, Unlimited Calls", "₹698/mo (x2)"),
        ("Services Subtotal", "", "₹2,196/mo"),
        ("Multi-Product Bundle Discount", "Consolidation discount (10%)", "- ₹220/mo"),
        ("GST (18% Statutory)", "Government telecom tax", "+ ₹356/mo"),
        ("Total Monthly Bill", "Single Consolidated Bill", "₹2,332/mo"),
        ("One-Time Setup Fee", "12-month contract", "₹1,000"),
        ("Setup Waiver Incentive", "24+ month contract option", "₹0 (Waived)")
    ]
    for i, (pname, psub, pcost) in enumerate(q_items):
        qy = 400 - i * 32
        is_total = "Total" in pname or "Subtotal" in pname
        c.setFillColor(GREEN if "Discount" in pname or "Waiver" in pname else (WHITE if is_total else LIGHT))
        c.setFont("Helvetica-Bold" if is_total else "Helvetica", 9)
        c.drawString(500, qy, pname)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(670, qy, psub)
        c.setFillColor(GREEN if "Discount" in pname or "Waiver" in pname else (AMBER if is_total else WHITE))
        c.setFont("Helvetica-Bold" if is_total else "Helvetica", 9)
        c.drawRightString(910, qy, pcost)
        
    c.setFillColor(colors.HexColor("#065F46"))
    c.roundRect(500, 60, 415, 38, 6, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawCentredString(707, 82, "💡 Transparent Pricing Advantage:")
    c.setFont("Helvetica", 8)
    c.drawCentredString(707, 68, "Saves ~35% vs fragmented local vendors · Single monthly invoice · No code jargon")

    c.showPage()
    
    # ==================== SLIDE 6 ====================
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    draw_header(c, "Slide 6: Business Case, Funnel Transformation & Partner Synergy", "Submission Requirement 3 (Case PDF p.4) · Key Question 4 & 5 · smb_leads.csv Analytics", 6)
    
    # Metrics Table
    draw_card(c, 25, 45, 450, 435, bg=SLATE, border=GREEN)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(45, 450, "Target Success Metrics (Key Question 5)")
    
    m_headers = ["Metric", "Baseline (smb_leads)", "Project Target"]
    c.setFillColor(CARD_BORDER)
    c.rect(45, 418, 410, 20, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(50, 424, m_headers[0])
    c.drawString(205, 424, m_headers[1])
    c.drawString(350, 424, m_headers[2])
    
    m_rows = [
        ("Lead-to-Activation", "7.4% (368 / 5,000)", ">= 15.0% (2x lift)"),
        ("Turnaround Time", "17.6 Days", "<= 5-7 Days"),
        ("Acquisition Cost (CAC)", "₹15,000 / activated lead", "<= ₹5,000 (3x lower)"),
        ("Status Chase Calls", "3.0 calls / lead", "< 0.2 (Order Tracker)"),
        ("6-Month Churn Rate", "15.2% baseline", "< 10.0%"),
        ("KYC Turnaround", "Days (Manual visits)", "< 5 Minutes (Digital)"),
        ("Customer NPS", "6.9 baseline", ">= 8.5")
    ]
    for i, (met, base, targ) in enumerate(m_rows):
        my = 385 - i * 36
        c.setFillColor(LIGHT)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(50, my + 10, met)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(205, my + 10, base)
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(350, my + 10, targ)
        
    c.setFillColor(DARK)
    c.roundRect(45, 60, 410, 65, 6, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(55, 108, "Unit Economics & Financial Return:")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(55, 92, "• Blended CAC reduced by ₹10,000 per customer across 15,000 quarterly leads.")
    c.drawString(55, 78, "• Net savings: ₹15 Cr/quarter in sales overhead against ~₹25K in serverless API costs.")
    c.drawString(55, 66, "• ROI on digital onboarding stack exceeds 6,000x.")
    
    # Right Box: Funnel & Partner Synergy
    draw_card(c, 495, 45, 440, 435, bg=SLATE, border=BLUE)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(515, 450, "Partner Synergy & ML Propensity (Key Question 4)")
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(515, 425, "1. Funnel Attrition Reality (smb_leads.csv):")
    
    fn_items = [
        ("Leads Generated", "5,000", 1.0, WHITE),
        ("Contacted", "3,406", 0.68, LIGHT),
        ("Needs Assessed", "1,974", 0.395, MUTED),
        ("Quote Accepted", "861", 0.172, AMBER),
        ("KYC Complete", "588", 0.118, AMBER),
        ("Activated", "368", 0.074, GREEN)
    ]
    for i, (fn_lbl, fn_cnt, fn_pct, fn_c) in enumerate(fn_items):
        fy = 395 - i * 22
        c.setFillColor(TRACK)
        c.rect(515, fy, 200, 16, fill=1, stroke=0)
        c.setFillColor(fn_c)
        c.rect(515, fy, 200 * fn_pct, 16, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(520, fy + 4, fn_lbl)
        c.drawRightString(710, fy + 4, fn_cnt)
        
    c.setFillColor(AMBER)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(725, 340, "⚠ Steepest drop: 44% at Quote stage")
    c.drawString(725, 328, "(Price high, quote took too long, complex)")
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(515, 240, "2. Field Force & Partner Collaboration Model:")
    partner_pts = [
        ("ML Propensity Scoring:", "Scikit-Learn Logistic Regression (ROC-AUC 0.69) scores leads on conversion propensity."),
        ("Warm Lead Recovery Queue:", "Unclosed leads who drop at Quote/Needs stages are passed to partners with full context."),
        ("Higher Commissions:", "Partners close warm, pre-qualified prospects instead of wasting time on cold visits."),
        ("No Partner Disintermediation:", "Partners retain commission attribution through digital promo codes and partner portals.")
    ]
    for i, (ph, pb) in enumerate(partner_pts):
        py = 215 - i * 36
        c.setFillColor(AMBER)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(515, py + 8, ph)
        c.setFillColor(LIGHT)
        c.setFont("Helvetica", 7.5)
        c.drawString(515, py - 4, pb[:70])
        c.drawString(515, py - 14, pb[70:140])

    c.showPage()
    
    # ==================== SLIDE 7 ====================
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    draw_header(c, "Slide 7: Phased Rollout, Privacy Governance & Next Steps", "Submission Requirements 3 & 4 (Case PDF p.4) · DPDP Act 2023 · Repository Links", 7)
    
    # 3-Phase Roadmap (Top)
    r_phases = [
        ("Phase 1: Pilot (M1–M3)", "5 Pilot Cities (Tier 1 & Tier 2)\nFocus on Micro Retail & Clinics\nSelf-serve web onboarding\nTarget: 2,000 activations\nValidate 5-day SLA guarantee", AMBER),
        ("Phase 2: Scale (M4–M6)", "Expand to 15 Metro & Tier-2 cities\nWhatsApp bot + Vernacular Voice\nDigiLocker & Aadhaar e-KYC integration\nPartner Back-Office Queue launch\nTarget: 10,000 activations", BLUE),
        ("Phase 3: National (M7–M12)", "Pan-India rollout across 28 circles\nAll MSME segments (inc. Manufacturers)\nCredit scoring & equipment financing\nFull billing ERP synchronization\nTarget: ₹500 Cr annual pipeline", GREEN)
    ]
    rw = 285
    for i, (rtitle, rdesc, rcolor) in enumerate(r_phases):
        rx = 25 + i * (rw + 17)
        draw_card(c, rx, H - 235, rw, 155, bg=SLATE, border=rcolor)
        c.setFillColor(rcolor)
        c.roundRect(rx + 10, H - 110, rw - 20, 20, 4, fill=1, stroke=0)
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(rx + rw/2, H - 103, rtitle)
        c.setFillColor(LIGHT)
        c.setFont("Helvetica", 8.5)
        for line_idx, line in enumerate(rdesc.split("\n")):
            c.drawString(rx + 14, H - 130 - line_idx * 16, line)
            
    # Bottom Left: 1-Page Privacy Note (DPDP Act 2023)
    draw_card(c, 25, 45, 440, 225, bg=SLATE, border=BLUE)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, 248, "🔒 DPDP Act 2023 Compliance & Privacy Note")
    
    priv_points = [
        ("Granular Explicit Consent:", "Pre-KYC checkbox in vernacular language stating exact telecom purpose."),
        ("Strict Data Minimisation:", "Only essential fields (GSTIN, legal name, date) extracted; raw documents deleted."),
        ("Automated PII Masking:", "PAN, GSTIN, consumer numbers masked in UI/logs (e.g. 37IHK*****L1ZS)."),
        ("30-Day Storage Limitation:", "Verified customer identity files permanently shredded 30 days post-activation."),
        ("Role-Based Partner Access:", "Field partners view propensity scores and business names only; zero raw PII access.")
    ]
    for i, (ph, pb) in enumerate(priv_points):
        py = 215 - i * 32
        c.setFillColor(AMBER)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(40, py + 8, f"✔ {ph}")
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(55, py - 3, pb)
        
    # Bottom Right: Code Repository & Deliverables Summary
    draw_card(c, 480, 45, 455, 225, bg=SLATE, border=GREEN)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(495, 248, "📦 Submission Deliverables & Repository Links")
    
    delivs = [
        ("GitHub Repository (Main Branch):", "https://github.com/anshraz27/Airtel_Sync.git", RED),
        ("Working Prototype Web Portal:", "FastAPI backend + Mobile Tailwind SPA (http://localhost:8000)", LIGHT),
        ("7-Slide Deck (PPTX Format):", "Airtel_SYNC_Udyam_Digital_7Slides.pptx", LIGHT),
        ("7-Slide Deck (PDF Format):", "Airtel_SYNC_Udyam_Digital_7Slides.pdf", LIGHT),
        ("Comprehensive Submission Doc:", "COMPREHENSIVE_SUBMISSION_DOC.md & privacy_note.md", LIGHT),
        ("Planted Traps Testing Key:", "All 12 Specimen applicants evaluated; planted traps caught 100%", GREEN)
    ]
    for i, (dh, db, dc) in enumerate(delivs):
        dy = 215 - i * 28
        c.setFillColor(WHITE if i==0 else AMBER)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(495, dy + 8, dh)
        c.setFillColor(dc)
        c.setFont("Helvetica-Bold" if i==0 else "Helvetica", 8)
        c.drawString(495, dy - 4, db)
        
    c.showPage()
    c.save()
    print(f"✅ Generated 7-Slide PDF successfully at: {PDF_PATH}")

if __name__ == "__main__":
    generate_pdf()
