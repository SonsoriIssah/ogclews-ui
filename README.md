# OG-CLEWS Policy Simulation UI

A desktop policy simulation tool built with PyQt5 that demonstrates
the integration of OG-Core (overlapping-generations macroeconomic
modelling) with CLEWS (Climate, Land, Energy and Water Systems modelling).

Built as a GSoC 2026 prototype for the UN OICT OG-CLEWS project.

## Features

- Country and time horizon selection (8 African countries, 10–50 year horizons)
- 5 adjustable policy levers: income tax, capital tax, government spending,
  renewable energy share, carbon tax
- Background simulation via QThread — UI never freezes
- Live progress bar and simulation log
- 3 interactive Plotly charts:
  - **MACRO** — GDP, Consumption, Welfare projections
  - **CLEWS** — Renewable energy share vs CO₂ emissions
  - **SCORES** — Policy impact summary

## Setup
```bash
# Requires Python 3.12
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Project Structure
```
ogclews_ui/
├── main.py          # Entry point
├── requirements.txt
└── app/
    ├── params.py    # Parameter definitions
    ├── worker.py    # QThread simulation engine
    ├── chart.py     # Plotly chart builders
    └── window.py    # MainWindow UI
```

## Related

- [OG-CLEWS](https://github.com/EAPD-DRB/OG-CLEWS)
- [OG-Core](https://github.com/PSLmodels/OG-Core)
- [MUIOGO](https://github.com/EAPD-DRB/MUIOGO)