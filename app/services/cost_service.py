# app/services/cost_service.py

# from decimal import Decimal

# PRINTERS = { # This can be moved to config or a simple DB table as per masterplan
#     "Prusa MK4S":  {"rate_g": 0.08, "rate_min": 0.01, "type": "Filament"},
#     "Prusa XL":    {"rate_g": 0.09, "rate_min": 0.011, "type": "Filament"},
#     "Raise3D":     {"rate_g": 0.10, "rate_min": 0.012, "type": "Filament"},
#     "Formlabs":    {"rate_g": 0.12, "rate_min": 0.008, "type": "Resin"},
# }

# MINIMUM_CHARGE = Decimal("3.00")

# def calculate_cost(printer_name: str, weight_g: float, time_min: int) -> Decimal:
#     printer_config = PRINTERS.get(printer_name)
#     if not printer_config:
#         raise ValueError(f"Unknown printer: {printer_name}")
    
#     cost = Decimal(str(weight_g * printer_config["rate_g"])) + Decimal(str(time_min * printer_config["rate_min"]))
#     cost = max(cost, MINIMUM_CHARGE)
#     return cost.quantize(Decimal("0.01")) # Format to 2 decimal places

# print("cost_service.py loaded (placeholder).") # Debug
pass 