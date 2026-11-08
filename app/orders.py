import uuid
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from app.quote import calculate_quote

# ponytail: In-memory dictionary for order tracking avoids setting up external database service during hackathon demo. Upgrade: PostgreSQL with Redis pub/sub.
_orders_db: Dict[str, Dict[str, Any]] = {}
REFERENCE_TODAY = date(2026, 7, 15)

def create_digital_order(
    business_name: str,
    contact_name: str,
    contact_phone: str,
    city: str,
    selected_items: List[Dict[str, Any]],
    contract_months: int = 12,
    kyc_applicant_id: Optional[str] = None
) -> Dict[str, Any]:
    """Creates a new digital order and schedules milestone dates based on product SLAs."""
    order_id = f"ORD-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    quote = calculate_quote(selected_items, contract_months)
    
    install_days = quote["estimated_activation_days"]
    target_activation_date = REFERENCE_TODAY + timedelta(days=install_days)
    
    milestones = [
        {
            "step": 1,
            "title": "Order Placed & Consent Logged",
            "date": str(REFERENCE_TODAY),
            "status": "COMPLETED",
            "desc": "Digital consent verified under DPDP Act 2023."
        },
        {
            "step": 2,
            "title": "Instant Registry & Smart KYC",
            "date": str(REFERENCE_TODAY),
            "status": "COMPLETED",
            "desc": "GSTIN and Udyam registry verified in real-time."
        },
        {
            "step": 3,
            "title": "Hardware Dispatch & Engineer Assigned",
            "date": str(REFERENCE_TODAY + timedelta(days=min(2, install_days))),
            "status": "IN_PROGRESS",
            "desc": "Router/SIM kit assigned to local field engineer."
        },
        {
            "step": 4,
            "title": "Site Installation & Line Provisioning",
            "date": str(REFERENCE_TODAY + timedelta(days=max(2, install_days - 1))),
            "status": "PENDING",
            "desc": f"Installation scheduled for {business_name} at {city} site."
        },
        {
            "step": 5,
            "title": "Go Live & Unified Bill Active",
            "date": str(target_activation_date),
            "status": "PENDING",
            "desc": f"High-speed service active. Single consolidated bill: ₹{quote['pricing_summary']['total_monthly_bill_inr']}/mo."
        }
    ]
    
    order_record = {
        "order_id": order_id,
        "created_at": str(REFERENCE_TODAY),
        "business_name": business_name,
        "contact_name": contact_name,
        "contact_phone": contact_phone,
        "city": city,
        "kyc_applicant_id": kyc_applicant_id,
        "quote": quote,
        "status": "PROVISIONING",
        "expected_activation_date": str(target_activation_date),
        "days_to_activation": install_days,
        "milestones": milestones
    }
    
    _orders_db[order_id] = order_record
    return order_record

def get_order_status(order_id: str) -> Optional[Dict[str, Any]]:
    """Fetches real-time status of an active customer order."""
    return _orders_db.get(order_id.strip().upper())

