import csv
import os
from typing import Dict, List, Any, Optional

# ponytail: Products are static 25 items in CSV. Load into memory on import; upgrade to cached DB query when catalogue is dynamic.
BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "YTL_TrackA_Udyam_Digital_Data")
CATALOGUE_PATH = os.path.join(BASE_DATA_DIR, "product_catalogue.csv")

_catalogue: Dict[str, Dict[str, Any]] = {}

def load_catalogue() -> Dict[str, Dict[str, Any]]:
    global _catalogue
    if _catalogue:
        return _catalogue
    
    with open(CATALOGUE_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["product_id"].strip()
            _catalogue[pid] = {
                "product_id": pid,
                "category": row["category"],
                "product_name": row["product_name"],
                "description": row["description"],
                "unit": row["unit"],
                "price_min": int(row["price_min_inr_per_month"]),
                "price_max": int(row["price_max_inr_per_month"]),
                "setup_fee": int(row["one_time_setup_inr"]),
                "min_contract_months": int(row["min_contract_months"]),
                "available_city_tiers": [int(t) for t in row["available_city_tiers"].split(";")],
                "min_employees": int(row["min_employees"]),
                "min_sites": int(row["min_sites"]),
                "requires_gstin": row["requires_gstin"].upper() == "Y",
                "requires_one_of": row["requires_one_of"].split("|") if row["requires_one_of"] else [],
                "typical_install_days": int(row["typical_install_days"]),
                "target_segments": row["target_segments"].split(";"),
            }
    return _catalogue

def evaluate_product_eligibility(
    product: Dict[str, Any],
    city_tier: int,
    employee_count: int,
    num_sites: int,
    has_active_gstin: bool,
    segment: Optional[str] = None,
    current_selected_product_ids: Optional[List[str]] = None
) -> tuple[bool, List[str]]:
    """Checks if a business profile qualifies for a specific product and returns (is_eligible, reasons)."""
    disqualifications = []
    
    # 1. City Tier check
    if city_tier not in product["available_city_tiers"]:
        disqualifications.append(f"Requires city tier {product['available_city_tiers']}, current is tier {city_tier}")
        
    # 2. Employee size check
    if employee_count < product["min_employees"]:
        disqualifications.append(f"Requires at least {product['min_employees']} employees (has {employee_count})")
        
    # 3. Site count check
    if num_sites < product["min_sites"]:
        disqualifications.append(f"Requires at least {product['min_sites']} sites (has {num_sites})")
        
    # 4. GSTIN requirement check
    if product["requires_gstin"] and not has_active_gstin:
        disqualifications.append("Requires an Active GSTIN registration")
        
    # 5. Dependency check (requires_one_of)
    if product["requires_one_of"]:
        selected = current_selected_product_ids or []
        has_dependency = any(dep in selected for dep in product["requires_one_of"])
        if not has_dependency:
            deps_str = " or ".join(product["requires_one_of"])
            disqualifications.append(f"Requires one base connectivity product ({deps_str}) in the bundle")
            
    return (len(disqualifications) == 0, disqualifications)

def get_eligible_products(
    city_tier: int,
    employee_count: int,
    num_sites: int,
    has_active_gstin: bool,
    segment: Optional[str] = None
) -> Dict[str, Any]:
    """Returns all standalone eligible products and dependent add-ons for a business."""
    catalogue = load_catalogue()
    eligible_base = []
    eligible_addons = []
    ineligible = []
    
    # Segment mapping shorthand
    seg_code = {
        "Micro retail & services": "micro",
        "Professional offices": "prof",
        "Small multi-site businesses": "multi",
        "Small manufacturers": "mfg"
    }.get(segment, segment.lower() if segment else None)

    for pid, p in catalogue.items():
        # Evaluate without dependency to see if it qualifies fundamentally
        eligible_no_deps, reasons_no_deps = evaluate_product_eligibility(
            product=p,
            city_tier=city_tier,
            employee_count=employee_count,
            num_sites=num_sites,
            has_active_gstin=has_active_gstin,
            segment=seg_code,
            current_selected_product_ids=p["requires_one_of"] # pretend satisfied to test fundamental eligibility
        )
        
        is_targeted = seg_code in p["target_segments"] if seg_code else True
        p_summary = {
            "product_id": pid,
            "category": p["category"],
            "product_name": p["product_name"],
            "description": p["description"],
            "price_min": p["price_min"],
            "price_max": p["price_max"],
            "setup_fee": p["setup_fee"],
            "unit": p["unit"],
            "install_days": p["typical_install_days"],
            "is_targeted": is_targeted,
            "requires_one_of": p["requires_one_of"]
        }

        if eligible_no_deps:
            if p["requires_one_of"]:
                eligible_addons.append(p_summary)
            else:
                eligible_base.append(p_summary)
        else:
            ineligible.append({"product_id": pid, "product_name": p["product_name"], "reasons": reasons_no_deps})

    return {
        "eligible_base_products": eligible_base,
        "eligible_addons": eligible_addons,
        "ineligible_products": ineligible,
    }

def build_curated_bundle(
    segment: str,
    city_tier: int,
    employee_count: int,
    num_sites: int,
    has_active_gstin: bool,
    needs_description: str = ""
) -> Dict[str, Any]:
    """Generates a high-fit starting bundle for the persona based on eligibility and historical SMB lead winners."""
    catalogue = load_catalogue()
    eligibility = get_eligible_products(city_tier, employee_count, num_sites, has_active_gstin, segment)
    base_ids = [p["product_id"] for p in eligibility["eligible_base_products"]]
    
    bundle_items = []
    
    # 1. Base connectivity recommendation
    if "P01" in base_ids and (city_tier == 2 or employee_count <= 5):
        bundle_items.append({"product_id": "P01", "quantity": 1}) # Biz Fibre 100
    elif "P02" in base_ids:
        bundle_items.append({"product_id": "P02", "quantity": 1}) # Biz Fibre 300
    elif "P04" in base_ids:
        bundle_items.append({"product_id": "P04", "quantity": 1}) # AirFiber
    elif "P05" in base_ids and employee_count >= 10:
        bundle_items.append({"product_id": "P05", "quantity": 1}) # Leased Line

    # 2. Add-on recommendation based on segment
    seg_lower = segment.lower()
    selected_pids = [b["product_id"] for b in bundle_items]
    
    if "retail" in seg_lower or "kirana" in seg_lower:
        # Micro retail needs: WhatsApp API (if GSTIN), Secure Wi-Fi, Postpaid
        if has_active_gstin and "P15" in [p["product_id"] for p in eligibility["eligible_base_products"]]:
            bundle_items.append({"product_id": "P15", "quantity": 1}) # WhatsApp API
        if "P22" in [p["product_id"] for p in eligibility["eligible_addons"]]:
            bundle_items.append({"product_id": "P22", "quantity": 1}) # Secure Wi-Fi
        if "P07" in base_ids:
            bundle_items.append({"product_id": "P07", "quantity": 1}) # Business Postpaid 299

    elif "prof" in seg_lower or "clinic" in seg_lower or "ca" in seg_lower:
        # Professional office needs: Cloud Email, Endpoint Security, Failover
        if "P16" in base_ids:
            bundle_items.append({"product_id": "P16", "quantity": max(2, min(employee_count, 10))}) # Email
        if "P20" in base_ids:
            bundle_items.append({"product_id": "P20", "quantity": max(2, min(employee_count, 10))}) # Antivirus
        if "P09" in [p["product_id"] for p in eligibility["eligible_addons"]]:
            bundle_items.append({"product_id": "P09", "quantity": 1}) # Failover

    elif "multi" in seg_lower or "restaurant" in seg_lower or num_sites > 1:
        # Multi-site: SD-WAN (if eligible), Cloud CCTV
        if has_active_gstin and "P10" in [p["product_id"] for p in eligibility["eligible_addons"]]:
            bundle_items.append({"product_id": "P10", "quantity": num_sites})
        if "P23" in [p["product_id"] for p in eligibility["eligible_addons"]]:
            bundle_items.append({"product_id": "P23", "quantity": min(num_sites * 2, 8)})

    # Calculate pricing
    total_monthly_min = 0
    total_monthly_max = 0
    total_setup = 0
    detailed_products = []
    max_install_days = 0

    for item in bundle_items:
        prod = catalogue[item["product_id"]]
        qty = item["quantity"]
        p_min = prod["price_min"] * qty
        p_max = prod["price_max"] * qty
        p_setup = prod["setup_fee"] * qty
        total_monthly_min += p_min
        total_monthly_max += p_max
        total_setup += p_setup
        max_install_days = max(max_install_days, prod["typical_install_days"])
        detailed_products.append({
            "product_id": prod["product_id"],
            "product_name": prod["product_name"],
            "unit": prod["unit"],
            "quantity": qty,
            "monthly_price_min": p_min,
            "monthly_price_max": p_max,
            "setup_fee": p_setup,
            "typical_install_days": prod["typical_install_days"]
        })

    return {
        "segment": segment,
        "bundle_items": detailed_products,
        "summary": {
            "monthly_total_min": total_monthly_min,
            "monthly_total_max": total_monthly_max,
            "monthly_recommended": round((total_monthly_min + total_monthly_max) / 2),
            "one_time_setup": total_setup,
            "estimated_delivery_days": max_install_days
        }
    }

