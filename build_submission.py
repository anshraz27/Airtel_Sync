"""
Airtel SYNC – Project Udyam Digital
7-Slide Detailed Submission Document
Builds: PPTX + PDF
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE
from copy import deepcopy
import lxml.etree as etree

OUT_DIR = r"c:\Users\thean\Desktop\airtel_digital"
PPT_PATH = os.path.join(OUT_DIR, "Airtel_SYNC_Udyam_Digital_7Slides.pptx")

# ── Colour palette ─────────────────────────────────────────────────────────
RED     = RGBColor(0xE5, 0x1B, 0x00)   # Airtel red
DARK    = RGBColor(0x0F, 0x17, 0x2A)   # Slide background
SLATE   = RGBColor(0x1E, 0x29, 0x3B)   # Card background
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT   = RGBColor(0xF1, 0xF5, 0xF9)
MUTED   = RGBColor(0x94, 0xA3, 0xB8)
GREEN   = RGBColor(0x10, 0xB9, 0x81)
AMBER   = RGBColor(0xF5, 0x9E, 0x0B)
BLUE    = RGBColor(0x38, 0xBD, 0xF8)

W = Inches(13.33)   # Widescreen 16:9
H = Inches(7.5)


# ── Helpers ────────────────────────────────────────────────────────────────
def new_prs() -> Presentation:
    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H
    return prs

def blank_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])   # completely blank

def fill_bg(slide, color: RGBColor):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def box(slide, x, y, w, h, bg_color=None, border_color=None, border_width=Pt(0)):
    """Add a plain rectangle shape."""
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.line.width = border_width
    if bg_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
    else:
        shape.fill.background()
    if border_color:
        shape.line.color.rgb = border_color
    else:
        shape.line.fill.background()
    return shape

def txt(slide, text, x, y, w, h, size=18, bold=False, color=WHITE,
        align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tb

def multiline_txt(slide, lines, x, y, w, h, size=14, bold=False, color=WHITE,
                  align=PP_ALIGN.LEFT, line_spacing=Pt(6)):
    """lines = list of (text, bold_override, color_override) or plain strings."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for idx, line in enumerate(lines):
        if isinstance(line, str):
            text, b, c = line, bold, color
        else:
            text, b, c = line
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = line_spacing
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = b
        run.font.color.rgb = c
    return tb

def label_value(slide, label, value, x, y, lw=2.2, vw=1.6, lsize=11, vsize=22):
    txt(slide, label, x, y+0.05, lw, 0.3, size=lsize, color=MUTED)
    txt(slide, value, x, y+0.35, vw, 0.55, size=vsize, bold=True, color=WHITE)

def header_bar(slide, title, subtitle=""):
    """Red left accent bar + title + subtitle."""
    box(slide, 0, 0, 0.12, H.inches, bg_color=RED)
    txt(slide, title,    0.25, 0.22, 9.0, 0.6, size=28, bold=True, color=WHITE)
    if subtitle:
        txt(slide, subtitle, 0.25, 0.82, 9.0, 0.4, size=13, color=MUTED)
    # Right pill for repo
    box(slide, 9.4, 0.25, 3.6, 0.52, bg_color=SLATE, border_color=RED, border_width=Pt(1))
    txt(slide, "GitHub: github.com/anshraz27/Airtel_Sync", 9.45, 0.38, 3.5, 0.3, size=9.5, bold=True, color=LIGHT, align=PP_ALIGN.CENTER)

def card(slide, x, y, w, h, title="", body_lines=None, title_color=WHITE,
         body_size=12, body_color=LIGHT, bg=SLATE, border=RED):
    box(slide, x, y, w, h, bg_color=bg, border_color=border, border_width=Pt(1.2))
    if title:
        txt(slide, title, x+0.15, y+0.12, w-0.3, 0.38, size=13, bold=True, color=title_color)
    if body_lines:
        multiline_txt(slide, body_lines, x+0.15, y+0.52, w-0.3,
                      h-0.65, size=body_size, color=body_color, line_spacing=Pt(4))

def bullet_block(slide, items, x, y, w, h, size=13, bullet="▸ ", color=LIGHT):
    lines = [(f"{bullet}{item}" if not item.startswith("  ") else item, False, color)
             for item in items]
    multiline_txt(slide, lines, x, y, w, h, size=size, color=color, line_spacing=Pt(5))

def funnel_bar(slide, label, value, pct, y, max_w=5.5, done=False):
    """Single horizontal funnel bar."""
    bar_w = max_w * pct
    color = GREEN if done else RED
    # Background track
    box(slide, 7.5, y, max_w, 0.38, bg_color=RGBColor(0x2D, 0x3B, 0x50))
    # Filled bar
    box(slide, 7.5, y, bar_w, 0.38, bg_color=color)
    # Label
    txt(slide, label,  7.1, y+0.04, 1.8, 0.32, size=11, color=LIGHT)
    txt(slide, value,  13.1, y+0.04, 1.2, 0.32, size=11, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)


# ══════════════════════════════════════════════════════════════════════════
# SLIDE 1 – Title / Problem Overview
# ══════════════════════════════════════════════════════════════════════════
def slide1(prs):
    sl = blank_slide(prs)
    fill_bg(sl, DARK)

    # Full-width red gradient strip on top
    box(sl, 0, 0, W.inches, 1.6, bg_color=RED)

    # Hackathon label
    txt(sl, "YTL HACKATHON 2026  ·  ENTERPRISE TRACK A",
        0.5, 0.12, 12.3, 0.35, size=11, color=RGBColor(0xFF,0xBB,0xAA), bold=False)

    # Main title
    txt(sl, "Project Udyam Digital",
        0.5, 0.42, 7.5, 0.72, size=40, bold=True, color=WHITE)

    txt(sl, "Making 6 Crore+ Indian MSMEs Go Digital in One Sitting",
        0.5, 1.12, 7.5, 0.45, size=18, color=RGBColor(0xFF,0xE0,0xDB))

    # GitHub Repo Banner Pill
    box(sl, 8.2, 0.45, 4.6, 0.75, bg_color=DARK, border_color=WHITE, border_width=Pt(1.2))
    txt(sl, "GitHub Code Repository (Main):", 8.35, 0.52, 4.3, 0.25, size=10, bold=True, color=RED)
    txt(sl, "https://github.com/anshraz27/Airtel_Sync", 8.35, 0.78, 4.3, 0.3, size=11, bold=True, color=WHITE)

    # Tagline strip
    box(sl, 0, 1.6, W.inches, 0.06, bg_color=RGBColor(0x7F, 0x0D, 0x00))

    # Four pillars
    pillars = [
        ("🤖", "AI Advisor",     "GenAI needs discovery\nin Hindi & English"),
        ("📋", "Quote & Checkout","Transparent pricing,\nzero hidden charges"),
        ("🛡️", "Smart KYC",      "Instant GSTIN/Udyam\nlookup + OCR + DPDP"),
        ("📦", "Order Tracker",   "Self-serve status,\neliminate 3× callbacks"),
    ]
    for i, (icon, ttl, desc) in enumerate(pillars):
        cx = 0.5 + i * 3.2
        box(sl, cx, 2.0, 2.9, 2.0, bg_color=SLATE,
            border_color=RED, border_width=Pt(1))
        txt(sl, icon, cx+1.1, 2.1, 0.8, 0.5, size=22, color=WHITE, align=PP_ALIGN.CENTER)
        txt(sl, ttl,  cx+0.1, 2.6, 2.7, 0.4, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(sl, desc, cx+0.1, 3.0, 2.7, 0.9, size=11, color=MUTED, align=PP_ALIGN.CENTER)

    # Problem stats bar
    box(sl, 0, 4.25, W.inches, 1.5, bg_color=SLATE)
    txt(sl, "The Problem at a Glance  (Source: smb_leads.csv · Case PDF p.5)",
        0.4, 4.3, 12.5, 0.4, size=12, color=MUTED)

    stats = [
        ("7.4%",     "Lead-to-Activation"),
        ("17.6 days","Avg Activation Time"),
        ("₹15,000",  "Cost per Acquired SMB"),
        ("3×",       "Status Calls per Order"),
        ("4.7×",     "GSTIN vs No-GSTIN\nActivation Rate"),
    ]
    for i, (val, lbl) in enumerate(stats):
        cx = 0.5 + i * 2.55
        txt(sl, val, cx, 4.65, 2.3, 0.6, size=24, bold=True, color=RED, align=PP_ALIGN.CENTER)
        txt(sl, lbl, cx, 5.2,  2.3, 0.4, size=10, color=MUTED, align=PP_ALIGN.CENTER)

    # Footer
    txt(sl, "Airtel SYNC · Digital Track · 7-Slide Submission · Code: https://github.com/anshraz27/Airtel_Sync · 2026",
        0, 7.1, W.inches, 0.35, size=10, color=MUTED, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════
# SLIDE 2 – Target Segments & Prioritisation
# ══════════════════════════════════════════════════════════════════════════
def slide2(prs):
    sl = blank_slide(prs)
    fill_bg(sl, DARK)
    header_bar(sl,
               "Slide 2: Target Segments & Prioritisation",
               "Key Question 1 (Case PDF p.3) · Source: smb_leads.csv + Appendix A2")

    segments = [
        {
            "icon": "🏪", "name": "Micro Retail & Services",
            "share": "55%  of SMB base", "examples": "Kirana, salon, pharmacy",
            "current": "Owner's mobile + hotspot, UPI QR",
            "needs": "Reliable internet for UPI/POS\nWhatsApp Business catalogue",
            "bundle": "P01 + P22 + P07  ≈  ₹1,947/mo",
            "priority": "TIER 1  ·  Highest Volume",
            "pc": AMBER,
        },
        {
            "icon": "🩺", "name": "Professional Offices",
            "share": "25%  of SMB base", "examples": "Clinic, CA firm, coaching",
            "current": "Home broadband, personal Gmail",
            "needs": "99.9% uptime, cloud email\nEndpoint security, 4G failover",
            "bundle": "P02 + P16 + P20 + P09  ≈  ₹4,813/mo",
            "priority": "TIER 2  ·  Highest ARPU",
            "pc": GREEN,
        },
        {
            "icon": "🏬", "name": "Small Multi-Site Businesses",
            "share": "15%  of SMB base", "examples": "Restaurant chain, 3-10 stores",
            "current": "Mixed ISPs, no central IT",
            "needs": "Single bill, SD-WAN\nCCTV, 4G failover per site",
            "bundle": "P02 + P10 + P23 + P09  ≈  ₹7,200/mo",
            "priority": "TIER 3  ·  High LTV",
            "pc": BLUE,
        },
        {
            "icon": "🏭", "name": "Small Manufacturers",
            "share": "5%  of SMB base", "examples": "Auto-parts, textile unit",
            "current": "Leased line or local ISP",
            "needs": "Dedicated ILL bandwidth\nIoT machine sensors (P24)",
            "bundle": "P05/P06 + P24 + P20  ≈  ₹12,000/mo",
            "priority": "TIER 4  ·  Specialist",
            "pc": RED,
        },
    ]

    for i, seg in enumerate(segments):
        cx = 0.25 + i * 3.25
        box(sl, cx, 1.35, 3.08, 5.65, bg_color=SLATE,
            border_color=seg["pc"], border_width=Pt(1.5))
        # Priority badge
        box(sl, cx, 1.35, 3.08, 0.38, bg_color=seg["pc"])
        txt(sl, seg["priority"], cx+0.08, 1.37, 2.9, 0.33,
            size=10, bold=True, color=DARK)
        txt(sl, seg["icon"] + "  " + seg["name"],
            cx+0.1, 1.78, 2.9, 0.42, size=13, bold=True, color=WHITE)
        txt(sl, seg["share"], cx+0.1, 2.2, 2.9, 0.3, size=11, color=seg["pc"], bold=True)
        txt(sl, "e.g. " + seg["examples"], cx+0.1, 2.5, 2.9, 0.28, size=10, color=MUTED)

        txt(sl, "Current Setup:", cx+0.1, 2.85, 2.9, 0.25, size=10, bold=True, color=MUTED)
        txt(sl, seg["current"],   cx+0.1, 3.1, 2.9, 0.4, size=10, color=LIGHT)

        txt(sl, "Key Digital Needs:", cx+0.1, 3.52, 2.9, 0.25, size=10, bold=True, color=MUTED)
        txt(sl, seg["needs"],         cx+0.1, 3.77, 2.9, 0.55, size=10, color=LIGHT)

        txt(sl, "Recommended Bundle:", cx+0.1, 4.38, 2.9, 0.25, size=10, bold=True, color=MUTED)
        txt(sl, seg["bundle"],         cx+0.1, 4.63, 2.9, 0.45, size=10, color=GREEN, bold=True)

    txt(sl, "Data insight: Leads with an active GSTIN convert at 9.6% vs 2.0% without — "
            "prioritise GSTIN-registered prospects across all segments.  (smb_leads.csv)",
        0.25, 7.05, 12.8, 0.35, size=10, color=AMBER)


# ══════════════════════════════════════════════════════════════════════════
# SLIDE 3 – Solution Architecture
# ══════════════════════════════════════════════════════════════════════════
def slide3(prs):
    sl = blank_slide(prs)
    fill_bg(sl, DARK)
    header_bar(sl,
               "Slide 3: Solution Architecture & Data Flow",
               "Submission Requirement 2 (Case PDF p.4) · Multi-layer, Airtel-scale design")

    # Layer boxes (left column labels)
    layers = [
        ("Mobile-First Web App",    "React / Tailwind · Hindi & English · PWA",        0.25, 1.35, SLATE, BLUE),
        ("FastAPI Gateway",         "REST API · CORS · PII Masking Middleware",          0.25, 2.25, SLATE, GREEN),
        ("Orchestration / AI",      "Advisor Agent · KYC Pipeline · Quote Engine",      0.25, 3.15, SLATE, AMBER),
        ("LLM / Vision",            "Qwen2.5-72B  |  Qwen2-VL-7B  (Free HF API)",      0.25, 4.05, SLATE, RED),
        ("Data & Registry Layer",   "GSTIN 3,534 recs · Udyam 2,723 recs · SQLite",    0.25, 4.95, SLATE, MUTED),
        ("Observability & Compliance","PII Masking · Consent Store · Audit Log (DPDP)", 0.25, 5.85, SLATE, MUTED),
    ]
    for lbl, sub, lx, ly, bg, bc in layers:
        box(sl, lx, ly, 4.3, 0.75, bg_color=bg, border_color=bc, border_width=Pt(1))
        txt(sl, lbl, lx+0.12, ly+0.07, 4.0, 0.33, size=12, bold=True, color=WHITE)
        txt(sl, sub, lx+0.12, ly+0.4, 4.0, 0.3,  size=10, color=MUTED)

    # Arrows between layers
    for ay in [2.1, 3.0, 3.9, 4.8, 5.7]:
        txt(sl, "↓", 2.15, ay, 0.4, 0.28, size=14, bold=True, color=RED, align=PP_ALIGN.CENTER)

    # Right panel: component responsibilities
    box(sl, 4.85, 1.35, 8.1, 5.25, bg_color=SLATE,
        border_color=RED, border_width=Pt(1))
    txt(sl, "Component Responsibilities & Key Decisions",
        5.0, 1.42, 7.8, 0.4, size=13, bold=True, color=WHITE)

    rows = [
        ("Eligibility Engine",   "Deterministic Python code — not LLM. Filters 25 products by city tier,\n"
                                 "employee count, sites, GSTIN status, dependency chain. Zero hallucination risk."),
        ("HF Advisor (LLM)",     "Qwen2.5-72B via HF Serverless Inference API. Stateful multi-turn. Falls back\n"
                                 "to offline rule engine so demo never fails even without token."),
        ("KYC Pipeline",         "Qwen2-VL-7B Vision OCR → field extraction → GSTIN Mod-36 checksum →\n"
                                 "registry lookup → cross-doc name match → 90-day address freshness gate."),
        ("GSTIN/Udyam Mock APIs","100% join to smb_leads.csv. Validates Active/Cancelled/Suspended.\n"
                                 "All 15-char GSTINs pass custom checksum, accept 'X' as 4th PAN char."),
        ("Propensity Model",     "Scikit-learn LogReg on 5,000 leads. ROC-AUC 0.69. Top features:\n"
                                 "has_gstin (+4.7×), segment, city_tier, annual_turnover_band."),
        ("Order Tracker",        "In-memory order store. Milestone dates = REFERENCE_DATE + typical_install_days\n"
                                 "from product_catalogue. Eliminates 3× customer status-chase calls."),
    ]
    for i, (comp, desc) in enumerate(rows):
        ry = 1.9 + i * 0.78
        txt(sl, comp, 5.0, ry, 2.6, 0.32, size=11, bold=True, color=AMBER)
        txt(sl, desc, 7.65, ry, 5.2, 0.6,  size=10, color=LIGHT)
        if i < len(rows)-1:
            box(sl, 5.0, ry+0.65, 7.75, 0.02, bg_color=RGBColor(0x2D,0x3B,0x50))

    txt(sl, "ponytail: Eligibility rules are code, not prompt — catches every ineligible recommendation before the LLM explains it.",
        0.25, 7.05, 12.8, 0.35, size=10, color=AMBER)


# ══════════════════════════════════════════════════════════════════════════
# SLIDE 4 – Smart KYC & Planted Trap Defences
# ══════════════════════════════════════════════════════════════════════════
def slide4(prs):
    sl = blank_slide(prs)
    fill_bg(sl, DARK)
    header_bar(sl,
               "Slide 4: Smart KYC Engine & Planted Trap Defences",
               "Build Challenge (Case PDF p.3) · Key Question 3 · DPDP Act 2023 Compliance")

    # Pipeline flow (top)
    steps = [
        ("1", "DPDP Consent\nGate",      "Explicit pre-KYC\nconsent checkbox\nPurpose stated\nLanguage of choice", BLUE),
        ("2", "HF Vision\nOCR",           "Qwen2-VL-7B\nField extraction\nHandles rotation\nHandles blur", RED),
        ("3", "Format\nValidation",       "GSTIN 15-char\nMod-36 checksum\nAccepts 'X' PAN\nUdyam regex", AMBER),
        ("4", "Registry\nLookup",         "Active / Cancelled\n/ Suspended check\nName & address\ncross-match", GREEN),
        ("5", "Cross-Doc\nValidation",    "GST Trade Name\nvs Address Proof\n90-day bill\nfreshness gate", BLUE),
        ("6", "PASS / REJECT\n+ Reason",  "Specific error\nper document\nActionable fix\nguidance shown", RED),
    ]
    for i, (num, ttl, desc, pc) in enumerate(steps):
        cx = 0.25 + i * 2.17
        box(sl, cx, 1.35, 1.95, 2.3, bg_color=SLATE,
            border_color=pc, border_width=Pt(1.5))
        txt(sl, num,  cx+0.08, 1.38, 0.5, 0.42, size=18, bold=True, color=pc)
        txt(sl, ttl,  cx+0.08, 1.75, 1.78, 0.52, size=11, bold=True, color=WHITE)
        txt(sl, desc, cx+0.08, 2.28, 1.78, 1.25, size=10, color=MUTED)
        if i < len(steps)-1:
            txt(sl, "→", cx+1.98, 2.1, 0.22, 0.4, size=16, bold=True, color=RED)

    # Planted traps grid
    txt(sl, "Planted KYC Traps — All Detected & Correctly Flagged",
        0.25, 3.82, 12.8, 0.4, size=14, bold=True, color=WHITE)

    traps = [
        ("K01", "Vindhya Tours", "Blank Udyam Reg. Number",
         "GSTIN 37I*****1ZS → Cancelled in registry",
         "udyam_certificate field empty → flagged MISSING_REGISTRATION_NUMBER", RED),
        ("K02", "Harmony Dental", "Rotated / Skewed Doc",
         "Canvas size 1446×1894 (wider than std A4)",
         "Orientation correction applied; OCR proceeds; Warning raised", AMBER),
        ("K04", "Saffron Dental", "Blurry / Degraded Image",
         "Edge-variance Laplacian score = 175.8",
         "Threshold = 300. Rejected with 'Please re-upload a clear copy' message", RED),
        ("K05", "Balaji Realty", "Entity Name Mismatch",
         "GST Trade Name: 'Balaji Dental Care LLP'",
         "Bill billed_to: 'Balaji Realty LLP' → NAME_MISMATCH fatal error", RED),
        ("K05", "Balaji Realty", "Missing Udyam Document",
         "K05 folder has only 3 of 4 required docs",
         "Warning: 'Udyam Certificate not provided; MSME benefits locked'", AMBER),
        ("ANY", "All Applicants", "Address Proof Age Gate",
         "Reference date: 2026-07-15 (from README)",
         "Utility bills older than 90 days → DOCUMENT_EXPIRED fatal error", RED),
    ]
    for i, (kid, biz, trap, evidence, action, pc) in enumerate(traps):
        row = i // 3
        col = i % 3
        cx = 0.25 + col * 4.35
        cy = 4.3 + row * 1.4
        box(sl, cx, cy, 4.15, 1.3, bg_color=SLATE,
            border_color=pc, border_width=Pt(1))
        txt(sl, f"{kid}  ·  {biz}",   cx+0.1, cy+0.07, 3.9, 0.3, size=11, bold=True, color=pc)
        txt(sl, f"⚠ {trap}",          cx+0.1, cy+0.38, 3.9, 0.28, size=10, bold=True, color=WHITE)
        txt(sl, evidence,              cx+0.1, cy+0.66, 3.9, 0.28, size=9,  color=MUTED)
        txt(sl, f"→ {action}",        cx+0.1, cy+0.94, 3.9, 0.28, size=9,  color=GREEN)

    txt(sl, "Privacy (DPDP Act 2023): Consent gate → PII masking in all logs & UI (e.g. 37IHK*****L1ZS) → "
            "30-day document shredding → Purpose limitation to broadband provisioning only.",
        0.25, 7.05, 12.8, 0.35, size=10, color=BLUE)


# ══════════════════════════════════════════════════════════════════════════
# SLIDE 5 – Conversational AI Advisor & Quote Builder
# ══════════════════════════════════════════════════════════════════════════
def slide5(prs):
    sl = blank_slide(prs)
    fill_bg(sl, DARK)
    header_bar(sl,
               "Slide 5: GenAI Advisor & Transparent Quote Builder",
               "Build Challenge (Case PDF p.3) · Key Question 2 · Multi-language, Eligibility-Safe")

    # Left column – Advisor
    box(sl, 0.25, 1.35, 6.1, 5.65, bg_color=SLATE,
        border_color=BLUE, border_width=Pt(1.2))
    txt(sl, "🤖  Conversational AI Advisor",
        0.4, 1.42, 5.8, 0.42, size=14, bold=True, color=BLUE)
    txt(sl, "Free Hugging Face LLM  ·  HF Serverless Inference API  ·  Zero API cost",
        0.4, 1.84, 5.8, 0.3, size=10, color=MUTED)

    adv_items = [
        ("Primary Model",      "Qwen/Qwen2.5-72B-Instruct (Recommended)"),
        ("HF Alternative 1",   "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"),
        ("HF Alternative 2",   "meta-llama/Llama-3.1-8B-Instruct (Ultra-low latency)"),
        ("HF Alternative 3",   "mistralai/Mistral-7B-Instruct-v0.3 (Multilingual)"),
        ("Languages",          "English · Hindi (Devanagari) · Marathi · Tamil"),
        ("Eligibility Guard",  "Deterministic Python code — not LLM. Checks 25 products for city tier,\n"
                               "employees, GSTIN, dependency rules before LLM explains the recommendation."),
        ("Fallback Engine",    "Offline rule-based advisor fires if HF API rate-limits.\n"
                               "Demo always works — even with no token or no network."),
        ("Key Questions Answered",
                               "Q1: Which segment first?  → Detected from free-text input\n"
                               "Q2: What bundle?         → Eligibility engine + LLM narration\n"
                               "Q3: Clear monthly price? → Passed directly to Quote Builder"),
    ]
    for i, (lbl, val) in enumerate(adv_items):
        ry = 2.2 + i * 0.63
        txt(sl, lbl+":", 0.4, ry, 2.0, 0.28, size=10, bold=True, color=AMBER)
        txt(sl, val,     2.45, ry, 3.8, 0.55, size=10, color=LIGHT)

    # Sample conversation bubble
    txt(sl, "Demo: Kirana Owner in Hindi",
        0.4, 6.42, 5.8, 0.28, size=10, color=MUTED, bold=True)
    box(sl, 0.4, 6.7, 5.7, 0.55, bg_color=RGBColor(0x14,0x2B,0x40), border_color=BLUE, border_width=Pt(1))
    txt(sl, '"मुझे लखनऊ में अपनी किराना दुकान के लिए WiFi और WhatsApp Business चाहिए।"',
        0.55, 6.74, 5.4, 0.42, size=10, color=LIGHT, italic=True)

    # Right column – Quote Builder
    box(sl, 6.6, 1.35, 6.5, 5.65, bg_color=SLATE,
        border_color=GREEN, border_width=Pt(1.2))
    txt(sl, "📋  Transparent Quote Builder",
        6.75, 1.42, 6.2, 0.42, size=14, bold=True, color=GREEN)
    txt(sl, "Single, consolidated monthly bill  ·  No hidden charges  ·  Toggle add-ons",
        6.75, 1.84, 6.2, 0.3, size=10, color=MUTED)

    quote_rows = [
        ("Biz Fibre 100  (P01)",              "per site × 1",  "₹999/mo",   False),
        ("Secure Wi-Fi + Guest Net  (P22)",   "per site × 1",  "₹499/mo",   False),
        ("Business Postpaid 299  (P07)",      "per line × 2",  "₹699/mo",   False),
        ("─────── Subtotal ───────",          "",              "₹2,197/mo", False),
        ("10% Consolidator Discount",         "(2+ products)", "−₹220",     True),
        ("GST 18% (Statutory)",               "",              "+₹356",     False),
        ("════ Total Monthly Bill ════",      "",              "₹2,333/mo", False),
        ("One-time Setup Fee",                "12-mo contract","₹1,000",    False),
        ("Setup Fee Waiver",                  "24+ mo contract","₹0",       True),
        ("Est. Activation Date",              "Fibre SLA 5 d", "2026-07-20",False),
    ]
    for i, (item, unit, price, hi) in enumerate(quote_rows):
        ry = 2.22 + i * 0.49
        col = GREEN if hi else (WHITE if "═" in item or "──" in item else LIGHT)
        bold = "═" in item or "──" in item
        txt(sl, item,  6.75, ry, 3.5, 0.42, size=10, bold=bold, color=col)
        txt(sl, unit,  10.3, ry, 1.5, 0.42, size=9,  color=MUTED)
        txt(sl, price, 11.75, ry, 1.2, 0.42, size=11, bold=bold, color=col, align=PP_ALIGN.RIGHT)

    txt(sl, "Contract options: 12 mo (std) · 24 mo (setup waived) · 36 mo",
        6.75, 7.05, 6.2, 0.3, size=10, color=MUTED)


# ══════════════════════════════════════════════════════════════════════════
# SLIDE 6 – Business Case: Metrics, ROI, Funnel
# ══════════════════════════════════════════════════════════════════════════
def slide6(prs):
    sl = blank_slide(prs)
    fill_bg(sl, DARK)
    header_bar(sl,
               "Slide 6: Business Case — Value, Metrics & Funnel Transformation",
               "Submission Requirement 3 (Case PDF p.4) · Key Question 5 · Source: smb_leads.csv")

    # Left – Metrics table
    box(sl, 0.25, 1.35, 6.3, 5.65, bg_color=SLATE,
        border_color=GREEN, border_width=Pt(1.2))
    txt(sl, "📊  Success Metrics & Targets  (Key Question 5)",
        0.4, 1.42, 6.0, 0.42, size=13, bold=True, color=GREEN)

    headers = ["Metric", "Baseline (Data)", "Target"]
    col_x   = [0.4, 2.3, 4.7]
    col_w   = [1.85, 2.35, 1.6]
    # Header row
    box(sl, 0.4, 1.9, 6.0, 0.35, bg_color=RGBColor(0x0F,0x2D,0x1A))
    for j, h in enumerate(headers):
        txt(sl, h, col_x[j], 1.93, col_w[j], 0.28,
            size=10, bold=True, color=GREEN)

    rows = [
        ("Lead-to-Activation Conv.",  "7.4%  (368/5,000)", "≥ 15%  (+2×)"),
        ("Time to Activation",        "17.6 days avg",      "≤ 7 days"),
        ("Acquisition Cost (CAC)",    "₹15,000 blended",   "≤ ₹5,000  (3×↓)"),
        ("6-Month Churn Rate",        "15.2%  (activated)", "≤ 10%"),
        ("Status-Chase Calls",        "3.0 / customer",     "< 0.2  (Tracker)"),
        ("KYC Completion Time",       "Days (manual)",      "< 5 minutes"),
        ("NPS Score",                 "6.9  (activated)",   "≥ 8.0"),
    ]
    for i, (m, b, t) in enumerate(rows):
        ry = 2.3 + i * 0.56
        bg = RGBColor(0x1A,0x27,0x1A) if i % 2 == 0 else SLATE
        box(sl, 0.4, ry, 6.0, 0.52, bg_color=bg)
        txt(sl, m, col_x[0], ry+0.07, col_w[0], 0.4, size=10, color=LIGHT)
        txt(sl, b, col_x[1], ry+0.07, col_w[1], 0.4, size=10, color=MUTED)
        txt(sl, t, col_x[2], ry+0.07, col_w[2], 0.4, size=10, bold=True, color=GREEN)

    # ROI summary
    box(sl, 0.4, 6.3, 6.0, 0.6, bg_color=RGBColor(0x0F,0x2D,0x1A))
    txt(sl, "ROI: LLM API ≈ ₹2/lead call.  5,000 leads/quarter = ₹10K in AI costs vs "
            "₹75M saved in CAC.  7,500× cost efficiency.",
        0.55, 6.37, 5.75, 0.45, size=10, color=GREEN)

    # Right – Funnel visualisation
    box(sl, 6.8, 1.35, 6.1, 5.65, bg_color=SLATE,
        border_color=RED, border_width=Pt(1.2))
    txt(sl, "📉  Acquisition Funnel  (Apr–Jun 2026 · Case PDF p.5)",
        6.95, 1.42, 5.9, 0.42, size=13, bold=True, color=WHITE)

    funnel_data = [
        ("Lead Generated",   "5,000",  1.00, WHITE),
        ("Contacted",        "3,406",  0.681, LIGHT),
        ("Needs Assessed",   "1,974",  0.395, MUTED),
        ("Quote Accepted",   "861",    0.172, AMBER),   # steepest drop
        ("KYC Complete",     "588",    0.118, AMBER),
        ("Activated",        "368",    0.074, RED),
    ]
    pcts_txt = [("−", "68%", "58%", "44%", "68%", "63%")]
    txt(sl, "Stage", 6.95, 1.95, 2.3, 0.3, size=10, bold=True, color=MUTED)
    txt(sl, "Count", 9.3,  1.95, 1.0, 0.3, size=10, bold=True, color=MUTED, align=PP_ALIGN.RIGHT)
    txt(sl, "Conv.", 10.3, 1.95, 0.9, 0.3, size=10, bold=True, color=MUTED, align=PP_ALIGN.RIGHT)

    conv_pcts = ["—", "68%", "58%", "⚠44%", "68%", "63%"]
    for i, (stage, count, frac, color) in enumerate(funnel_data):
        ry = 2.3 + i * 0.65
        bar_w = frac * 3.5
        box(sl, 6.95, ry, 3.5, 0.45, bg_color=RGBColor(0x2D,0x3B,0x50))
        box(sl, 6.95, ry, bar_w, 0.45, bg_color=color)
        txt(sl, stage,         6.95, ry+0.08, 2.0, 0.3, size=10, color=DARK if frac > 0.3 else LIGHT)
        txt(sl, count,         9.3,  ry+0.08, 1.0, 0.3, size=11, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)
        txt(sl, conv_pcts[i], 10.3, ry+0.08, 0.9, 0.3, size=10, color=AMBER if "⚠" in conv_pcts[i] else MUTED, align=PP_ALIGN.RIGHT)

    # Steepest drop callout
    box(sl, 6.95, 5.65, 5.9, 0.9, bg_color=RGBColor(0x3A,0x1A,0x00))
    txt(sl, "⚠ Steepest Drop: 44% conversion at Quote stage",
        7.1, 5.69, 5.7, 0.3, size=11, bold=True, color=AMBER)
    txt(sl, "Root causes from drop reasons: 'Price too high' (414), 'Quote too complex' (206),\n"
            "'Quote took too long' (179).  Direct fix: Our instant, transparent quote builder.",
        7.1, 5.98, 5.7, 0.5, size=10, color=LIGHT)

    txt(sl, "Partner Synergy: ML propensity model (ROC-AUC 0.69) surfaces warm leads for field partners, "
            "protecting commissions and channelling effort to highest-intent unclosed prospects.",
        0.25, 7.05, 12.8, 0.35, size=10, color=BLUE)


# ══════════════════════════════════════════════════════════════════════════
# SLIDE 7 – Rollout, Privacy, Risks & Next Steps
# ══════════════════════════════════════════════════════════════════════════
def slide7(prs):
    sl = blank_slide(prs)
    fill_bg(sl, DARK)
    header_bar(sl,
               "Slide 7: Rollout, Data Privacy & Risk Mitigation",
               "Submission Requirements 3 & 4 (Case PDF p.4) · DPDP Act 2023 · Stretch Goals Delivered")

    # Row 1: Rollout phases
    phases = [
        ("Phase 1  (M1–M3)",
         "🏙️ Pilot: 5 Cities",
         "Lucknow, Jaipur, Kolkata,\nKochi, Coimbatore (Tier 1+2)\n"
         "Segments: Micro Retail + Prof.\n"
         "Channel: Digital ads + QR kits\n"
         "Target: 2,000 activations"),
        ("Phase 2  (M4–M6)",
         "🗣️ Vernacular Voice & WhatsApp",
         "Hindi · Tamil · Marathi · Telugu\n"
         "voice advisor + WhatsApp bot\n"
         "DigiLocker pilot integration\n"
         "Partner back-office rollout\n"
         "Target: 15 cities"),
        ("Phase 3  (M7–M12)",
         "🌏 National Scale",
         "All 28 circles, all segments\n"
         "Official DigiLocker + e-Sign\n"
         "100% paperless onboarding\n"
         "MSME-tailored credit scoring\n"
         "Target: ₹500Cr ARR pipeline"),
    ]
    for i, (phase, title, body) in enumerate(phases):
        cx = 0.25 + i * 4.35
        box(sl, cx, 1.35, 4.15, 2.65, bg_color=SLATE,
            border_color=RED, border_width=Pt(1.2))
        box(sl, cx, 1.35, 4.15, 0.38, bg_color=RED)
        txt(sl, phase, cx+0.1, 1.37, 3.95, 0.3, size=11, bold=True, color=WHITE)
        txt(sl, title, cx+0.1, 1.78, 3.95, 0.38, size=12, bold=True, color=WHITE)
        txt(sl, body,  cx+0.1, 2.18, 3.95, 1.75, size=10, color=LIGHT)

    # Row 2: Privacy note + stretch goals
    # Privacy (left)
    box(sl, 0.25, 4.2, 6.4, 2.8, bg_color=SLATE,
        border_color=BLUE, border_width=Pt(1.2))
    txt(sl, "🔒  1-Page Privacy Note (DPDP Act 2023)",
        0.4, 4.27, 6.1, 0.42, size=13, bold=True, color=BLUE)
    privacy_items = [
        "Explicit Consent Gate before any KYC document is processed (purpose & language)",
        "Data Minimisation: Only 3–5 fields extracted per doc; raw image shredded post-verification",
        "PII Masking in ALL logs & UI: 37IHK*****L1ZS · Consumer no: 948****625",
        "Purpose Limitation: Data bound ONLY to broadband provisioning (never 3rd-party marketing)",
        "Retention Policy: 30-day auto-deletion for verified docs; 14-day purge for unclosed leads",
        "Role-Based Access: Partners see propensity scores only; no raw KYC documents",
    ]
    bullet_block(sl, privacy_items, 0.4, 4.74, 6.1, 2.1, size=10, bullet="✔ ", color=LIGHT)

    # Deliverables & Code Repository (right)
    box(sl, 6.9, 4.2, 6.1, 2.8, bg_color=SLATE,
        border_color=GREEN, border_width=Pt(1.2))
    txt(sl, "📦  Code Repository & Deliverables Summary",
        7.05, 4.27, 5.8, 0.42, size=13, bold=True, color=GREEN)
    deliverables = [
        "GitHub Repo (Main): https://github.com/anshraz27/Airtel_Sync.git",
        "FastAPI Backend + Mobile Tailwind SPA (Running on port 8000)",
        "Free Hugging Face LLM (Qwen2.5-72B) & Vision OCR (Qwen2-VL-7B)",
        "All 12 Specimen KYC Applicants Verified (Planted Traps 100% Caught)",
        "ML Propensity Scoring (ROC-AUC 0.69) & Partner Warm Lead Queue",
        "Complete 7-Slider Submission Document in both PPTX and PDF formats"
    ]
    bullet_block(sl, deliverables, 7.05, 4.75, 5.8, 2.1, size=9.5, bullet="✔ ", color=LIGHT)

    txt(sl, "Field Force Integration: Digital channel is additive — partners receive scored warm leads, "
            "not cold calls. Commission model preserved. Code: https://github.com/anshraz27/Airtel_Sync",
        0.25, 7.05, 12.8, 0.35, size=10, color=GREEN)


# ══════════════════════════════════════════════════════════════════════════
# MAIN BUILD
# ══════════════════════════════════════════════════════════════════════════
def build_all():
    prs = new_prs()
    print("Building Slide 1 – Title & Problem Overview...")
    slide1(prs)
    print("Building Slide 2 – Target Segments & Prioritisation...")
    slide2(prs)
    print("Building Slide 3 – Solution Architecture...")
    slide3(prs)
    print("Building Slide 4 – Smart KYC & Planted Traps...")
    slide4(prs)
    print("Building Slide 5 – AI Advisor & Quote Builder...")
    slide5(prs)
    print("Building Slide 6 – Business Case & Funnel...")
    slide6(prs)
    print("Building Slide 7 – Rollout, Privacy & Risks...")
    slide7(prs)
    prs.save(PPT_PATH)
    print(f"\n✅  Saved PPTX  →  {PPT_PATH}")

    # Generate companion PDF
    from generate_pdf_slides import generate_pdf
    generate_pdf()
    print("✅  Saved PDF   →  c:\\Users\\thean\\Desktop\\airtel_digital\\Airtel_SYNC_Udyam_Digital_7Slides.pdf")
    return PPT_PATH

if __name__ == "__main__":
    build_all()

