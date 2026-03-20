# app/window.py

import os
import threading
import http.server
import socketserver

from PyQt5.QtCore    import Qt, QThread, QUrl, pyqtSlot
from PyQt5.QtGui     import QPalette, QColor
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QLabel, QPushButton,
    QComboBox, QDoubleSpinBox, QProgressBar,
    QPlainTextEdit, QTabWidget
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

from app.params import COUNTRIES, POLICY_LEVERS, TIME_HORIZONS, DEFAULT_HORIZON
from app.worker import SimWorker
from app.chart  import build_macro_chart, build_clews_chart, build_scores_chart


BG      = "#0f1117"
SURFACE = "#1a1d27"
BORDER  = "#2a2d3a"
ACCENT  = "#00e5ff"
ACCENT2 = "#ff6b35"
TEXT    = "#e8eaf0"
DIM     = "#6b7280"
GREEN   = "#00c9a7"

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHART_PORT = 18745

STYLESHEET = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: 'Courier New', monospace;
    font-size: 12px;
}}
QGroupBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 10px;
    font-weight: bold;
    color: {ACCENT};
    letter-spacing: 1px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}
QLabel {{
    color: {TEXT};
    background: transparent;
}}
QDoubleSpinBox, QSpinBox, QComboBox {{
    background-color: {BG};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
    color: {TEXT};
    min-width: 100px;
}}
QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    selection-background-color: {ACCENT};
    selection-color: {BG};
}}
QPushButton {{
    background-color: {ACCENT};
    color: {BG};
    border: none;
    border-radius: 5px;
    padding: 8px 22px;
    font-weight: bold;
    letter-spacing: 1px;
}}
QPushButton:hover    {{ background-color: #33ecff; }}
QPushButton:pressed  {{ background-color: #009fbf; }}
QPushButton:disabled {{ background-color: {BORDER}; color: {DIM}; }}
QPushButton#stopBtn  {{ background-color: {ACCENT2}; color: #fff; }}
QPushButton#stopBtn:hover {{ background-color: #ff8556; }}
QProgressBar {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    background: {BG};
    height: 14px;
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 3px;
}}
QPlainTextEdit {{
    background-color: {BG};
    border: 1px solid {BORDER};
    border-radius: 4px;
    color: {GREEN};
    font-size: 11px;
    padding: 4px;
}}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    background: {SURFACE};
    border-radius: 6px;
}}
QTabBar::tab {{
    background: {BG};
    color: {DIM};
    padding: 6px 18px;
    border: 1px solid {BORDER};
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    font-size: 11px;
    letter-spacing: 1px;
}}
QTabBar::tab:selected {{
    background: {SURFACE};
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}
"""


def _start_chart_server():
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None
    os.chdir(BASE_DIR)
    httpd = socketserver.TCPServer(("127.0.0.1", CHART_PORT), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()


def _chart_url(filename: str) -> QUrl:
    return QUrl(f"http://127.0.0.1:{CHART_PORT}/{filename}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OG-CLEWS  ·  Policy Simulation UI")
        self.resize(1200, 750)
        self._thread = None
        self._worker = None
        _start_chart_server()
        self._build_ui()
        self.setStyleSheet(STYLESHEET)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)
        root.addWidget(self._make_left_panel(),  stretch=0)
        root.addWidget(self._make_right_panel(), stretch=1)

    def _make_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(270)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self._make_scenario_group())
        layout.addWidget(self._make_policy_group())
        layout.addWidget(self._make_control_group())
        layout.addWidget(self._make_log_group())
        return panel

    def _make_scenario_group(self) -> QGroupBox:
        grp = QGroupBox("SCENARIO")
        g   = QGridLayout(grp)
        g.setSpacing(8)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet(f"color:{DIM}; font-size:11px;")
            return l

        self._combo_country = QComboBox()
        self._combo_country.addItems(COUNTRIES)
        g.addWidget(lbl("COUNTRY"), 0, 0)
        g.addWidget(self._combo_country, 0, 1)

        self._combo_horizon = QComboBox()
        for h in TIME_HORIZONS:
            self._combo_horizon.addItem(f"{h} years", h)
        self._combo_horizon.setCurrentIndex(TIME_HORIZONS.index(DEFAULT_HORIZON))
        g.addWidget(lbl("HORIZON"), 1, 0)
        g.addWidget(self._combo_horizon, 1, 1)

        return grp

    def _make_policy_group(self) -> QGroupBox:
        grp = QGroupBox("POLICY LEVERS")
        g   = QGridLayout(grp)
        g.setSpacing(8)
        self._policy_widgets = {}

        for row, (key, cfg) in enumerate(POLICY_LEVERS.items()):
            lbl = QLabel(cfg["label"])
            lbl.setStyleSheet(f"color:{DIM}; font-size:10px;")
            lbl.setWordWrap(True)

            spin = QDoubleSpinBox()
            spin.setRange(cfg["min"], cfg["max"])
            spin.setValue(cfg["default"])
            spin.setSingleStep(cfg["step"])
            if "%" in cfg["label"]:
                spin.setSuffix(" %")
            elif "$" in cfg["label"]:
                spin.setPrefix("$ ")

            self._policy_widgets[key] = spin
            g.addWidget(lbl,  row, 0)
            g.addWidget(spin, row, 1)

        return grp

    def _make_control_group(self) -> QGroupBox:
        grp = QGroupBox("CONTROL")
        vl  = QVBoxLayout(grp)
        vl.setSpacing(8)

        self._btn_run  = QPushButton("▶  RUN SIMULATION")
        self._btn_stop = QPushButton("■  STOP")
        self._btn_stop.setObjectName("stopBtn")
        self._btn_stop.setEnabled(False)

        self._progress = QProgressBar()
        self._progress.setValue(0)
        self._progress.setFormat("%p%")

        btn_row = QHBoxLayout()
        btn_row.addWidget(self._btn_run)
        btn_row.addWidget(self._btn_stop)
        vl.addLayout(btn_row)
        vl.addWidget(self._progress)

        self._btn_run.clicked.connect(self._on_run)
        self._btn_stop.clicked.connect(self._on_stop)

        return grp

    def _make_log_group(self) -> QGroupBox:
        grp = QGroupBox("LOG")
        vl  = QVBoxLayout(grp)
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(200)
        self._log.setMinimumHeight(150)
        vl.addWidget(self._log)
        return grp

    def _make_right_panel(self) -> QWidget:
        panel  = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("OG-CLEWS  POLICY SIMULATION")
        header.setStyleSheet(
            f"color:{ACCENT}; font-size:15px; font-weight:bold;"
            f"letter-spacing:3px; padding:4px 0px 8px 2px;"
        )
        layout.addWidget(header)

        self._tabs        = QTabWidget()
        self._view_macro  = QWebEngineView()
        self._view_clews  = QWebEngineView()
        self._view_scores = QWebEngineView()

        self._tabs.addTab(self._view_macro,  "MACRO")
        self._tabs.addTab(self._view_clews,  "CLEWS")
        self._tabs.addTab(self._view_scores, "SCORES")

        for view in [self._view_macro, self._view_clews, self._view_scores]:
            view.setHtml(self._placeholder_html())

        layout.addWidget(self._tabs)
        return panel

    def _placeholder_html(self) -> str:
        return f"""
        <html>
        <body style="background:{BG}; display:flex; align-items:center;
                     justify-content:center; height:100vh; margin:0;">
          <p style="color:{DIM}; font-family:Courier New,monospace;
                    font-size:16px; letter-spacing:2px;">
            RUN SIMULATION TO SEE RESULTS
          </p>
        </body>
        </html>
        """

    @pyqtSlot()
    def _on_run(self):
        params = {
            "country":           self._combo_country.currentText(),
            "horizon":           self._combo_horizon.currentData(),
            "income_tax_rate":   self._policy_widgets["income_tax_rate"].value(),
            "capital_tax_rate":  self._policy_widgets["capital_tax_rate"].value(),
            "govt_spending_gdp": self._policy_widgets["govt_spending_gdp"].value(),
            "renewable_share":   self._policy_widgets["renewable_share"].value(),
            "carbon_tax":        self._policy_widgets["carbon_tax"].value(),
        }

        self._log.clear()
        self._progress.setValue(0)
        self._btn_run.setEnabled(False)
        self._btn_stop.setEnabled(True)

        for view in [self._view_macro, self._view_clews, self._view_scores]:
            view.setHtml(self._placeholder_html())

        self._thread = QThread()
        self._worker = SimWorker(params)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._progress.setValue)
        self._worker.log.connect(self._append_log)
        self._worker.result.connect(self._on_result)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    @pyqtSlot()
    def _on_stop(self):
        if self._worker:
            self._worker.stop()

    @pyqtSlot(object)
    def _on_result(self, results: dict):
        charts = {
            "_chart_macro.html":  build_macro_chart(results),
            "_chart_clews.html":  build_clews_chart(results),
            "_chart_scores.html": build_scores_chart(results),
        }

        for filename, html in charts.items():
            path = os.path.join(BASE_DIR, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)

        self._view_macro.load(_chart_url("_chart_macro.html"))
        self._view_clews.load(_chart_url("_chart_clews.html"))
        self._view_scores.load(_chart_url("_chart_scores.html"))
        self._tabs.setCurrentIndex(0)

    @pyqtSlot()
    def _on_finished(self):
        self._btn_run.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._worker = None

    @pyqtSlot(str)
    def _on_error(self, tb: str):
        self._log.appendPlainText("ERROR:\n" + tb)
        self._btn_run.setEnabled(True)
        self._btn_stop.setEnabled(False)

    @pyqtSlot(str)
    def _append_log(self, text: str):
        self._log.appendPlainText(text)
        sb = self._log.verticalScrollBar()
        sb.setValue(sb.maximum())
