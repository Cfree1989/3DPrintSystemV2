# app/services/cost_service.py

from decimal import Decimal

# Printer configuration as per masterplan Section 5.5
PRINTERS = {
    "prusa_mk4s": {"rate_g": 0.08, "rate_min": 0.01, "type": "Filament", "display_name": "Prusa MK4S"},
    "prusa_xl": {"rate_g": 0.09, "rate_min": 0.011, "type": "Filament", "display_name": "Prusa XL"},
    "raise3d_pro2plus": {"rate_g": 0.10, "rate_min": 0.012, "type": "Filament", "display_name": "Raise3D Pro 2 Plus"},
    "formlabs_form3": {"rate_g": 0.12, "rate_min": 0.008, "type": "Resin", "display_name": "Formlabs Form 3"},
}

MINIMUM_CHARGE = Decimal("3.00")

def calculate_cost(printer_key: str, weight_g: float, time_min: int) -> Decimal:
    """
    Calculate printing cost based on printer rates and enforce minimum charge.
    
    Args:
        printer_key: Key from PRINTERS dict (e.g., "prusa_mk4s")
        weight_g: Weight in grams
        time_min: Time in minutes
    
    Returns:
        Cost as Decimal rounded to 2 decimal places, enforcing minimum charge
    
    Raises:
        ValueError: If printer_key is not found
    """
    printer_config = PRINTERS.get(printer_key)
    if not printer_config:
        raise ValueError(f"Unknown printer: {printer_key}")
    
    # Calculate base cost
    weight_cost = Decimal(str(weight_g * printer_config["rate_g"]))
    time_cost = Decimal(str(time_min * printer_config["rate_min"]))
    base_cost = weight_cost + time_cost
    
    # Enforce minimum charge
    final_cost = max(base_cost, MINIMUM_CHARGE)
    
    return final_cost.quantize(Decimal("0.01"))

def get_printer_display_name(printer_key: str) -> str:
    """Get the display name for a printer key."""
    printer_config = PRINTERS.get(printer_key)
    return printer_config["display_name"] if printer_config else printer_key

def get_printer_type(printer_key: str) -> str:
    """Get the print type (Filament/Resin) for a printer key."""
    printer_config = PRINTERS.get(printer_key)
    return printer_config["type"] if printer_config else "Unknown"

# print("cost_service.py loaded (placeholder).") # Debug
pass 