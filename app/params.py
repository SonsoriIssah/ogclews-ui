# app/params.py
# Defines all simulation parameters for the OG-CLEWS UI

COUNTRIES = [
    "Ghana", "Nigeria", "Kenya", "South Africa",
    "Ethiopia", "Tanzania", "Egypt", "Morocco"
]

POLICY_LEVERS = {
    "income_tax_rate": {
        "label": "Income Tax Rate (%)",
        "min": 0.0, "max": 60.0, "default": 25.0, "step": 0.5,
    },
    "capital_tax_rate": {
        "label": "Capital Tax Rate (%)",
        "min": 0.0, "max": 50.0, "default": 15.0, "step": 0.5,
    },
    "govt_spending_gdp": {
        "label": "Govt Spending (% GDP)",
        "min": 5.0, "max": 60.0, "default": 20.0, "step": 0.5,
    },
    "renewable_share": {
        "label": "Renewable Energy Share (%)",
        "min": 0.0, "max": 100.0, "default": 30.0, "step": 1.0,
    },
    "carbon_tax": {
        "label": "Carbon Tax ($/tonne)",
        "min": 0.0, "max": 200.0, "default": 10.0, "step": 5.0,
    },
}

TIME_HORIZONS = [10, 20, 30, 50]
DEFAULT_HORIZON = 30