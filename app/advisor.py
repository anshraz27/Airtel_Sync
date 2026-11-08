import os
import json
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional
from app.eligibility import build_curated_bundle, get_eligible_products, load_catalogue

# ponytail: Use stdlib urllib instead of langchain/openai packages to avoid dependency hell and run anywhere in <10ms.
# ponytail: Fallback rule-based advisor ensures 100% demo resilience if HF rate-limits or offline. Upgrade: Local vLLM/Ollama.

HF_PRIMARY_MODEL = "Qwen/Qwen2.5-72B-Instruct"
HF_ALTERNATIVES = [
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "meta-llama/Llama-3.1-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3"
]

ADVISOR_SYSTEM_PROMPT = """You are 'Airtel Udyam Digital Advisor' for Accel Business / Airtel SYNC.
Your job is to advise Indian small business owners (kirana stores, clinics, coaching institutes, multi-site restaurants, small manufacturers) in plain, jargon-free language (Hindi, English, or Hinglish).
Always recommend transparent bundles tailored to their size, budget, and business type.
Never pitch products that require a GSTIN if the user doesn't have an active GSTIN.
Be warm, concise, and explain *why* each product is included."""

def parse_user_profile(user_text: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    """Lightweight entity and intent extractor from user conversation."""
    combined = " ".join([h.get("content", "") for h in history] + [user_text]).lower()
    
    # 1. Segment detection
    segment = "Micro retail & services"
    if any(k in combined for k in ["clinic", "doctor", "hospital", "lab", "dental", "ca firm", "consultant", "office", "school", "coaching"]):
        segment = "Professional offices"
    elif any(k in combined for k in ["restaurant chain", "multi-site", "branch", "multiple store", "retail chain", "outlets"]):
        segment = "Small multi-site businesses"
    elif any(k in combined for k in ["factory", "manufacturing", "plant", "textile", "workshop", "auto part", "machinery"]):
        segment = "Small manufacturers"
    elif any(k in combined for k in ["kirana", "shop", "salon", "pharmacy", "retail", "store", "bakery", "dukaan"]):
        segment = "Micro retail & services"

    # 2. City tier detection
    tier = 2
    if any(k in combined for k in ["delhi", "mumbai", "bengaluru", "bangalore", "chennai", "hyderabad", "kolkata", "pune", "ahmedabad", "tier 1", "tier-1"]):
        tier = 1

    # 3. Employee count detection
    employees = 3
    for word in combined.split():
        if word.isdigit():
            val = int(word)
            if 1 <= val <= 200:
                employees = val
                break

    # 4. Sites count
    sites = 1
    if "site" in combined or "branch" in combined or "store" in combined:
        for word in combined.split():
            if word.isdigit() and int(word) <= 20:
                sites = int(word)

    # 5. GSTIN availability
    has_gstin = False
    if "gst" in combined or "gstin" in combined:
        if not any(neg in combined for neg in ["no gst", "without gst", "don't have gst", "nahi hai", "not have"]):
            has_gstin = True

    # 6. Language preference
    lang = "English"
    hindi_keywords = ["namaste", "chahiye", "dukaan", "kitna", "kya", "madad", "bhai", "hai", "mujhe",
                      "नमस्ते", "दुकान", "किराने", "चाहिए", "कितना", "हमे", "मुझे", "व्यापार"]
    if any(k in combined for k in hindi_keywords):
        lang = "Hindi"

    return {
        "segment": segment,
        "city_tier": tier,
        "employee_count": employees,
        "num_sites": sites,
        "has_active_gstin": has_gstin,
        "preferred_language": lang
    }

def call_huggingface_llm(
    prompt_messages: List[Dict[str, str]],
    model_name: str = HF_PRIMARY_MODEL,
    hf_token: Optional[str] = None
) -> Optional[str]:
    """Calls Hugging Face Serverless Inference API (Chat Completions router)."""
    token = hf_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        return None

    # Modern Hugging Face Router endpoint
    url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": prompt_messages,
        "temperature": 0.4,
        "max_tokens": 600
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
    except Exception as e:
        # Silently fall back to deterministic response generator
        pass
    return None

def generate_advisor_response(
    user_message: str,
    conversation_history: List[Dict[str, str]],
    hf_token: Optional[str] = None,
    model_name: str = HF_PRIMARY_MODEL
) -> Dict[str, Any]:
    """Orchestrates advisor reasoning: extracts profile, evaluates eligibility, bundles items, and formats advice."""
    profile = parse_user_profile(user_message, conversation_history)
    
    # 1. Deterministic eligibility & curated bundle calculation
    bundle = build_curated_bundle(
        segment=profile["segment"],
        city_tier=profile["city_tier"],
        employee_count=profile["employee_count"],
        num_sites=profile["num_sites"],
        has_active_gstin=profile["has_active_gstin"]
    )
    
    eligibility_info = get_eligible_products(
        city_tier=profile["city_tier"],
        employee_count=profile["employee_count"],
        num_sites=profile["num_sites"],
        has_active_gstin=profile["has_active_gstin"],
        segment=profile["segment"]
    )

    # 2. Formulate system + context prompt for HF LLM
    context_str = f"""
Detected Business Profile:
- Segment: {profile['segment']}
- City Tier: {profile['city_tier']}
- Employees: {profile['employee_count']}
- Sites: {profile['num_sites']}
- GSTIN Registered: {profile['has_active_gstin']}
- Language: {profile['preferred_language']}

Recommended Bundle:
- Items: {', '.join([f"{b['product_name']} (x{b['quantity']})" for b in bundle['bundle_items']])}
- Monthly Price: ₹{bundle['summary']['monthly_recommended']} (Range: ₹{bundle['summary']['monthly_total_min']} - ₹{bundle['summary']['monthly_total_max']})
- One-time setup: ₹{bundle['summary']['one_time_setup']}
- Delivery/Activation: ~{bundle['summary']['estimated_delivery_days']} days
"""

    messages = [
        {"role": "system", "content": ADVISOR_SYSTEM_PROMPT + "\n\n" + context_str},
    ]
    for h in conversation_history[-4:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": user_message})

    # Try Hugging Face LLM
    hf_response = call_huggingface_llm(messages, model_name=model_name, hf_token=hf_token)

    # If HF response unavailable, generate transparent native response
    if not hf_response:
        prod_names = [f"**{b['product_name']}**" for b in bundle['bundle_items']]
        if profile["preferred_language"] == "Hindi":
            hf_response = (
                f"नमस्ते! आपके व्यवसाय ({profile['segment']}) के लिए हमने यह विशेष डिजिटल बंडल तैयार किया है:\n\n"
                f"📦 **सुझाया गया बंडल:** {', '.join(prod_names)}\n"
                f"💰 **मासिक शुल्क:** ₹{bundle['summary']['monthly_recommended']}/माह (कोई छुपा हुआ चार्ज नहीं)\n"
                f"⚡ **शुरुआती सेटअप शुल्क:** ₹{bundle['summary']['one_time_setup']}\n"
                f"⏱️ **चालू होने का समय:** लगभग {bundle['summary']['estimated_delivery_days']} कार्यदिवस\n\n"
                f"यह बंडल आपके काम के लिए सुपरफ़ास्ट इंटरनेट और व्यावसायिक टूल्स उपलब्ध कराएगा। क्या आप इस कोटेशन को देखना और कस्टमाइज़ करना चाहेंगे?"
            )
        else:
            hf_response = (
                f"Welcome! Based on your profile ({profile['segment']}, {profile['employee_count']} employees in Tier {profile['city_tier']}), "
                f"we recommend the following zero-friction digital bundle:\n\n"
                f"📦 **Curated Bundle:** {', '.join(prod_names)}\n"
                f"💰 **Transparent Monthly Price:** ₹{bundle['summary']['monthly_recommended']}/month (est. range ₹{bundle['summary']['monthly_total_min']} - ₹{bundle['summary']['monthly_total_max']})\n"
                f"⚡ **One-time Setup Fee:** ₹{bundle['summary']['one_time_setup']}\n"
                f"⏱️ **Expected Activation:** ~{bundle['summary']['estimated_delivery_days']} business days\n\n"
                f"Every product in this bundle is 100% verified against your eligibility. You can customize add-ons in the next step."
            )

    return {
        "text": hf_response,
        "profile": profile,
        "bundle": bundle,
        "available_addons": eligibility_info["eligible_addons"],
        "ineligible_products": eligibility_info["ineligible_products"],
        "model_used": model_name if hf_token else "Deterministic Advisor Engine (HF Fallback)"
    }
