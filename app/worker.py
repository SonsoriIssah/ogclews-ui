# app/worker.py

import time
import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot


class SimWorker(QObject):

    progress  = pyqtSignal(int)
    log       = pyqtSignal(str)
    result    = pyqtSignal(object)
    finished  = pyqtSignal()
    error     = pyqtSignal(str)

    def __init__(self, params: dict):
        super().__init__()
        self.params   = params
        self._running = True

    def stop(self):
        self._running = False

    @pyqtSlot()
    def run(self):
        try:
            self._do_run()
        except Exception:
            import traceback
            self.error.emit(traceback.format_exc())
            self.finished.emit()

    def _do_run(self):
        p       = self.params
        years   = np.arange(1, p["horizon"] + 1)
        n       = len(years)
        results = {}

        self.log.emit(f"► Simulating {p['country']}  |  horizon={p['horizon']} yrs")
        time.sleep(0.1)

        # ── Stage 1: Macro model ──────────────────────────────────────────
        self.log.emit("  [1/4] Running overlapping-generations macro model…")
        gdp, consumption, welfare = [], [], []

        tax_drag    = 1 - (p["income_tax_rate"] / 100) * 0.4
        spend_boost = 1 + (p["govt_spending_gdp"] / 100) * 0.15
        base_growth = 0.035

        for i, yr in enumerate(years):
            if not self._running:
                self._emit_cancelled()
                return
            noise    = np.random.normal(0, 0.004)
            gdp_val  = (1 + base_growth + noise) ** yr * tax_drag * spend_boost
            cons_val = gdp_val * (0.62 - p["capital_tax_rate"] / 500)
            welf_val = np.log(cons_val + 1) * (1 - p["income_tax_rate"] / 300)
            gdp.append(gdp_val)
            consumption.append(cons_val)
            welfare.append(welf_val)
            self.progress.emit(int(25 * (i + 1) / n))
            time.sleep(0.03)

        results["years"]       = years
        results["gdp"]         = np.array(gdp)
        results["consumption"] = np.array(consumption)
        results["welfare"]     = np.array(welfare)
        self.log.emit("  ✔ Macro model complete.")

        # ── Stage 2: CLEWS model ──────────────────────────────────────────
        self.log.emit("  [2/4] Running CLEWS energy-water-land model…")
        renewable_share, co2_emissions = [], []
        renew_target = p["renewable_share"] / 100
        carbon_tax   = p["carbon_tax"]

        for i, yr in enumerate(years):
            if not self._running:
                self._emit_cancelled()
                return
            rs  = min(
                renew_target * (1 - np.exp(-0.1 * yr)) + np.random.normal(0, 0.01),
                1.0
            )
            co2 = (1 - rs) * np.exp(-carbon_tax / 200) * (1 / (1 + 0.02 * yr))
            renewable_share.append(rs * 100)
            co2_emissions.append(co2)
            self.progress.emit(25 + int(25 * (i + 1) / n))
            time.sleep(0.03)

        results["renewable_share"] = np.array(renewable_share)
        results["co2_emissions"]   = np.array(co2_emissions)
        self.log.emit("  ✔ CLEWS model complete.")

        # ── Stage 3: Policy scoring ───────────────────────────────────────
        self.log.emit("  [3/4] Scoring policy impact…")
        time.sleep(0.3)

        final_gdp_growth = float(
            np.mean(np.diff(results["gdp"]) / results["gdp"][:-1]) * 100
        )
        final_co2_drop = float(
            (results["co2_emissions"][0] - results["co2_emissions"][-1])
            / results["co2_emissions"][0] * 100
        )
        welfare_gain = float(
            (results["welfare"][-1] - results["welfare"][0])
            / results["welfare"][0] * 100
        )

        results["scores"] = {
            "GDP Growth (avg %)":   round(final_gdp_growth, 2),
            "CO₂ Reduction (%)":    round(final_co2_drop,   2),
            "Welfare Gain (%)":     round(welfare_gain,     2),
            "Renewable Target Met": (
                "Yes" if results["renewable_share"][-1] >= p["renewable_share"] * 0.9
                else "No"
            ),
        }
        self.progress.emit(90)
        self.log.emit("  ✔ Policy scoring complete.")

        # ── Stage 4: Finalise ─────────────────────────────────────────────
        self.log.emit("  [4/4] Finalising results…")
        time.sleep(0.2)
        results["country"] = p["country"]
        results["horizon"] = p["horizon"]

        self.progress.emit(100)
        self.log.emit("✔ Simulation complete.")
        self.result.emit(results)
        self.finished.emit()

    def _emit_cancelled(self):
        self.log.emit("✖ Simulation cancelled.")
        self.finished.emit()