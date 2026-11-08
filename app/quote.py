from typing import Dict, List, Any
from app.eligibility import load_catalogue

# ponytail: Pure math pricing function; zero DB dependency. Upgrade: Dynamic ERP rate card.

def calculate_quote(
    selected_items: List[Dict[str, Any]],
    contract_months: int = 12
) -> Dict[str, Any]:
    """Calculates transparent monthly bundle price, setup fees, GST, and multi-product discount."""
    catalogue = load_catalogue()
    
    line_items = []
    monthly_subtotal = 0
    setup_subtotal = 0
    max_install_days = 1
    
    for item in selected_items:
        pid = item["product_id"]
        if pid not in catalogue:
            continue
        prod = catalogue[pid]
        qty = int(item.get("quantity", 1))
        
        # Base unit price (midpoint of range)
        unit_price = round((prod["price_min"] + prod["price_max"]) / 2)
        item_monthly = unit_price * qty
        item_setup = prod["setup_fee"] * qty
        
        monthly_subtotal += item_monthly
        setup_subtotal += item_setup
        max_install_days = max(max_install_days, prod["typical_install_days"])
        
        line_items.append({
            "product_id": pid,
            "product_name": prod["product_name"],
            "category": prod["category"],
            "unit": prod["unit"],
            "quantity": qty,
            "unit_price": unit_price,
            "item_monthly_total": item_monthly,
            "setup_fee": item_setup,
            "install_days": prod["typical_install_days"]
        })
        
    # Multi-product bundle discount (encourages consolidation from fragmented vendors)
    discount_pct = 0.0
    if len(line_items) >= 4:
        discount_pct = 0.15 # 15% off for 4+ services
    elif len(line_items) >= 2:
        discount_pct = 0.10 # 10% off for 2-3 services
        
    discount_amount = round(monthly_subtotal * discount_pct)
    discounted_monthly = monthly_subtotal - discount_amount
    
    # 18% GST standard in India telecom
    gst_monthly = round(discounted_monthly * 0.18)
    total_monthly_with_tax = discounted_monthly + gst_monthly
    
    # Setup fee waiver for 24+ month contracts
    final_setup_fee = setup_subtotal
    if contract_months >= 24:
        final_setup_fee = 0
        
    return {
        "line_items": line_items,
        "pricing_summary": {
            "monthly_subtotal": monthly_subtotal,
            "bundle_discount_pct": int(discount_pct * 100),
            "bundle_discount_inr": discount_amount,
            "discounted_monthly": discounted_monthly,
            "gst_18_pct": gst_monthly,
            "total_monthly_bill_inr": total_monthly_with_tax,
            "one_time_setup_fee_inr": final_setup_fee,
            "setup_discount_applied": contract_months >= 24 and setup_subtotal > 0,
            "contract_months": contract_months
        },
        "estimated_activation_days": max_install_days,
        "estimated_vendor_savings_inr": round(monthly_subtotal * 0.35) # Savings vs fragmented multi-vendor
    }

