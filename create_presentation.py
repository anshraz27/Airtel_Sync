import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_deck():
    template_path = r"c:\Users\thean\Desktop\airtel_digital\Submission Template_Sync.pptx"
    output_path = r"c:\Users\thean\Desktop\airtel_digital\Airtel_SYNC_Udyam_Digital_Submission.pptx"
    
    prs = Presentation(template_path)
    
    # Color palette
    AIRTEL_RED = RGBColor(225, 25, 0)
    DARK_BG = RGBColor(15, 23, 42)
    TEXT_LIGHT = RGBColor(248, 250, 252)
    TEXT_MUTED = RGBColor(148, 163, 184)
    ACCENT_EMERALD = RGBColor(16, 185, 129)

    slides_content = [
        {
            "title": "Airtel SYNC · Project Udyam Digital",
            "subtitle": "Making 6 Crore+ Indian MSMEs Go Digital in One Sitting\nEnterprise Track A · Digital Journey Prototype & Business Case",
            "bullets": [
                "Team: Senior Software Engineering & Product Advisory",
                "Vision: Eliminate the 93% SMB drop-off with conversational discovery, zero-friction Smart KYC, and transparent unified billing."
            ]
        },
        {
            "title": "The Core Problem: A Broken Acquisition Funnel",
            "subtitle": "Why Accel Business Loses 92.6% of SMB Leads (smb_leads.csv Analysis)",
            "bullets": [
                "Steepest Drop at Quote Stage: Conversion drops to 44% from needs assessment due to complex PDF codes & opaque pricing.",
                "High Blended CAC (₹15,000/lead): Field sales visits for small accounts yield low ROI against median ₹6,900/mo spend.",
                "Sluggish 17.6-Day Activation: Paper-heavy KYC and manual verification cause 3+ anxious customer follow-up calls.",
                "The GSTIN Disparity: Leads with valid GSTINs activate at 9.6% vs only 2.0% without, indicating high intent but severe documentation friction."
            ]
        },
        {
            "title": "Target Personas & Priority Segments",
            "subtitle": "Data-Driven Segmentation of India's 6 Crore+ Enterprise Base",
            "bullets": [
                "1. Micro Retail & Services (55% Base, Very High Price Sensitivity): Kiranas, salons, bakeries. Need: Reliable UPI WiFi, WhatsApp catalogue, single bill under ₹2,000/mo.",
                "2. Professional Offices (25% Base, Medium Sensitivity): Clinics, CA firms. Need: 99.9% uptime, cloud email, automated endpoint security, 4G/5G failover.",
                "3. Small Multi-Site Retailers (15% Base, Low-Medium Sensitivity): Restaurant chains. Need: SD-WAN, cloud CCTV, single consolidated dashboard & invoice.",
                "4. Small Manufacturers (5% Base, Low Price Sensitivity): Auto parts units. Need: High-throughput leased line (P05/P06), IoT machine sensors (P24)."
            ]
        },
        {
            "title": "Product Definition: The Digital Journey MVP",
            "subtitle": "Four Integrated Modules Built for Mobile in Vernacular Languages",
            "bullets": [
                "1. Conversational AI Advisor: Powered by free Hugging Face LLM (Qwen2.5-72B / Llama-3.3-70B) in Hindi & English with deterministic eligibility enforcement.",
                "2. Transparent Quote Builder: Interactive add-on toggling, instant multi-product bundle discount (10-15%), and 0 setup fee on 24-month contracts.",
                "3. Smart KYC Engine: Hugging Face Vision OCR + instant mock GSTIN/Udyam lookup, catching planted problems (blur, rotation, name mismatch).",
                "4. Live Order Tracker: Self-serve milestone status tracking with SLA-backed activation dates, completely eliminating customer status chases."
            ]
        },
        {
            "title": "System Architecture: Multi-Layer & Resilient",
            "subtitle": "Defensible Engineering Designed for Airtel Scale",
            "bullets": [
                "Frontend: Mobile-first responsive web application with multi-language toggle (English & Hindi).",
                "Orchestration & API: FastAPI asynchronous gateway with modular endpoints for registry lookups, quote math, and order provisioning.",
                "AI/ML Intelligence: Hugging Face Serverless Inference API for conversation & OCR, backed by a deterministic local engine for 100% demo resilience.",
                "Data & Verification Layer: O(1) in-memory registries for GSTIN (3,534 records) and Udyam (2,723 records) with Mod-36 checksum verification."
            ]
        },
        {
            "title": "Smart KYC & Planted Problem Defenses",
            "subtitle": "Flawless Performance on Hackathon Specimen Test Traps",
            "bullets": [
                "K01 (Dental): Automatically caught Cancelled GSTIN status in registry AND blank Udyam registration number.",
                "K02 (Harmony): Detected skewed/rotated document canvas; applied automated orientation correction without breaking OCR.",
                "K04 (Saffron): Evaluated image sharpness (edge variance 175.8 vs 300 cutoff); rejected unreadable blurry upload with guidance.",
                "K05 (Balaji): Cross-validated entity names; flagged mismatch between GST Trade Name and Address Proof Billed Entity.",
                "DPDP Act 2023 Compliance: Pre-KYC explicit consent screen, PII masking across logs/UI, and 30-day automated data shredding."
            ]
        },
        {
            "title": "Synergy with Existing Field Force & Partners",
            "subtitle": "Transforming Cold Calling into an AI-Powered Warm Lead Pipeline",
            "bullets": [
                "ML Propensity Scoring: Trained Scikit-Learn Logistic Regression on 5,000 historical leads (ROC-AUC: 0.69) to prioritize high-intent drops.",
                "Warm Partner Recovery Queue: Unclosed leads who dropped due to 'Price too high' or 'No time for visit' are routed to local channel partners with pre-filled context.",
                "Higher Partner Commissions: Partners spend less time on manual paperwork and focus purely on closing warm, digitally pre-qualified prospects.",
                "Omnichannel Continuity: If an SMB owner abandons the web flow, their digital basket is saved for instant partner retrieval."
            ]
        },
        {
            "title": "Business Impact & Unit Economics",
            "subtitle": "Projected ROI and Funnel Transformation for Accel Business",
            "bullets": [
                "Acquisition Cost Reduction: Slashes blended CAC from ₹15,000 to ₹5,000 per activated SMB (3x improvement).",
                "Conversion Doubled: Increases lead-to-activation conversion from 7.4% to 15.0%+ via instant quotes and frictionless KYC.",
                "Cycle Time Compressed: Reduces lead-to-activation turnaround from 17.6 days to <= 5 days for wireless and <= 7 days for fibre.",
                "Support Call Elimination: Drops status chase calls from 3.0 to < 0.2 per customer via self-serve order tracking.",
                "Consolidated SMB Savings: Customers save 30-35% compared to purchasing fragmented broadband, SIMs, and software from multiple vendors."
            ]
        },
        {
            "title": "Phased Rollout & Scalability Roadmap",
            "subtitle": "From Hackathon Prototype to National Deployment",
            "bullets": [
                "Phase 1 (Months 1-3): Pilot in 5 Tier 1 & 2 cities focusing on Micro Retail and Professional Offices via digital ads and QR kits.",
                "Phase 2 (Months 4-6): Roll out regional language voice front-end (Hindi, Tamil, Marathi, Telugu) and WhatsApp conversational bot integration.",
                "Phase 3 (Months 7-12): National rollout across all 28 circles; integrate official DigiLocker API and e-Sign for 100% paperless enterprise onboarding."
            ]
        },
        {
            "title": "Risk Mitigation & Governance Summary",
            "subtitle": "Defensible Solutions for Every Hackathon Evaluation Metric",
            "bullets": [
                "AI Hallucination Risk: Mitigated via deterministic eligibility code rules; LLM only explains recommendations, it never invents products.",
                "Regulatory Compliance: Full adherence to DPDP Act 2023 with purpose limitation, data minimisation, and automated retention limits.",
                "Channel Partner Friction: Mitigated by providing partners with warm, scored leads and commission protection on digital drop-offs.",
                "Winning Edge: Working end-to-end prototype, free Hugging Face AI integration, planted trap immunity, and rigorous data-backed strategy."
            ]
        }
    ]

    # Clear existing slides and populate 10 professional slides
    # If template has slides, we update them or add new ones
    while len(prs.slides) > 0:
        rId = prs.slides._sldIdLst[0].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[0]

    blank_layout = prs.slide_layouts[6] # blank layout

    for idx, sc in enumerate(slides_content):
        slide = prs.slides.add_slide(blank_layout)
        
        # Title Box
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.5), Inches(1.2))
        tf = title_box.text_frame
        tf.word_wrap = True
        
        p_title = tf.paragraphs[0]
        p_title.text = sc["title"]
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = AIRTEL_RED
        
        p_sub = tf.add_paragraph()
        p_sub.text = sc["subtitle"]
        p_sub.font.size = Pt(14)
        p_sub.font.color.rgb = RGBColor(100, 116, 139)
        p_sub.space_before = Pt(4)

        # Bullets Box
        content_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.5), Inches(4.8))
        c_tf = content_box.text_frame
        c_tf.word_wrap = True

        for b_idx, bullet in enumerate(sc["bullets"]):
            p = c_tf.paragraphs[0] if b_idx == 0 else c_tf.add_paragraph()
            p.text = "• " + bullet
            p.font.size = Pt(15)
            p.font.color.rgb = RGBColor(30, 41, 59)
            p.space_after = Pt(12)
            p.line_spacing = 1.25

    prs.save(output_path)
    print(f"Presentation saved successfully with {len(prs.slides)} slides to {output_path}")

if __name__ == "__main__":
    create_deck()

