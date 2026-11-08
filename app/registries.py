import csv
import os
import re
from typing import Optional, Dict, Any

# ponytail: In-memory dict lookup is O(1) and under 1MB RAM; avoids heavy DB ORM setup for hackathon speed. Upgrade: Postgres indexed table.
BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "YTL_TrackA_Udyam_Digital_Data")
CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{4}[A-Z0-9][0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")
UDYAM_REGEX = re.compile(r"^UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}$")

_gstin_cache: Dict[str, Dict[str, Any]] = {}
_udyam_cache: Dict[str, Dict[str, Any]] = {}

def validate_gstin_format(gstin: str) -> tuple[bool, str]:
    gstin = gstin.strip().upper()
    if len(gstin) != 15:
        return False, "GSTIN must be exactly 15 characters"
    if not GSTIN_REGEX.match(gstin):
        return False, "GSTIN format invalid (State code + PAN with 'X' + Entity + 'Z' + Checksum)"
    
    # Mod-36 Luhn-like checksum validation as per Indian GST specifications
    factor = 1
    total = 0
    for char in gstin[:-1]:
        val = CHARS.find(char)
        if val == -1:
            return False, f"Invalid character '{char}' in GSTIN"
        product = val * factor
        quotient, remainder = divmod(product, 36)
        total += quotient + remainder
        factor = 2 if factor == 1 else 1
    
    check_code = (36 - (total % 36)) % 36
    if CHARS[check_code] != gstin[-1]:
        return False, f"GSTIN checksum mismatch (expected {CHARS[check_code]}, got {gstin[-1]})"
    
    return True, "Valid GSTIN format and checksum"

def validate_udyam_format(udyam: str) -> tuple[bool, str]:
    udyam = udyam.strip().upper()
    if not UDYAM_REGEX.match(udyam):
        return False, "Udyam number must follow format UDYAM-XX-00-XXXXXXX"
    return True, "Valid Udyam format"

def _load_registries():
    global _gstin_cache, _udyam_cache
    if _gstin_cache and _udyam_cache:
        return

    gst_file = os.path.join(BASE_DATA_DIR, "mock_gstin_registry.csv")
    if os.path.exists(gst_file):
        with open(gst_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                _gstin_cache[row["gstin"].strip().upper()] = row

    udyam_file = os.path.join(BASE_DATA_DIR, "mock_udyam_registry.csv")
    if os.path.exists(udyam_file):
        with open(udyam_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                _udyam_cache[row["udyam_number"].strip().upper()] = row

def lookup_gstin(gstin: str) -> Dict[str, Any]:
    _load_registries()
    valid, msg = validate_gstin_format(gstin)
    if not valid:
        return {"valid_format": False, "error": msg, "found": False}
    
    record = _gstin_cache.get(gstin.strip().upper())
    if not record:
        return {"valid_format": True, "found": False, "error": "GSTIN not found in registry"}
    
    return {
        "valid_format": True,
        "found": True,
        "status": record["status"],  # Active, Cancelled, Suspended
        "is_active": record["status"].lower() == "active",
        "legal_name": record["legal_name"],
        "trade_name": record["trade_name"],
        "constitution": record["constitution"],
        "principal_place_of_business": record["principal_place_of_business"],
        "state": record["state"],
        "registration_date": record["registration_date"],
    }

def lookup_udyam(udyam_number: str) -> Dict[str, Any]:
    _load_registries()
    valid, msg = validate_udyam_format(udyam_number)
    if not valid:
        return {"valid_format": False, "error": msg, "found": False}
    
    record = _udyam_cache.get(udyam_number.strip().upper())
    if not record:
        return {"valid_format": True, "found": False, "error": "Udyam number not found in registry"}
    
    return {
        "valid_format": True,
        "found": True,
        "enterprise_name": record["enterprise_name"],
        "enterprise_type": record["enterprise_type"],
        "major_activity": record["major_activity"],
        "nic_description": record["nic_description"],
        "state": record["state"],
        "city": record["city"],
        "date_of_registration": record["date_of_registration"],
    }

