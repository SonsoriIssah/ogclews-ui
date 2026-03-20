# app/chart.py

import os
import tempfile
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BG      = "#0f1117"
SURFACE = "#1a1d27"
GRID    = "#2a2d3a"
TEXT    = "#e8eaf0"
DIM     = "#6b7280"

COLORS = {
    "gdp":        "#00e5ff",
    "consumption":"#00c9a7",
    "welfare":    "#ffd166",
    "renewable":  "#06d6a0",
    "co2":        "#ff6b35",
}

LAYOUT_BASE = dict(
    paper_bgcolor = BG,
    plot_bgcolor  = SURFACE,
    font          = dict(family="Courier New, monospace", color=TEXT, size=11),
    margin        = dict(l=50, r=20, t=50, b=40),
    legend        = dict(
        bgcolor     = SURFACE,
        bordercolor = GRID,
        borderwidth = 1,
    ),
)


def _axis(title_text=""):
    """Return a clean axis dict compatible with Plotly 6."""
    d = dict(
        gridcolor     = GRID,
        zerolinecolor = GRID,
        tickfont      = dict(color=DIM, size=10),
        color         = DIM,
    )
    if title_text:
        d["title_text"] = title_text
    return d


def _to_html(fig) -> str:
    return fig.to_html(
        full_html        = True,
        include_plotlyjs = True,
        config           = {"displayModeBar": False},
    )


def build_macro_chart(results: dict) -> str:
    years = results["years"]

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("GDP (index)", "Consumption (index)", "Welfare (utils)"),
    )

    fig.add_trace(go.Scatter(
        x=years, y=results["gdp"],
        name="GDP",
        line=dict(color=COLORS["gdp"], width=2),
        fill="tozeroy", fillcolor="rgba(0,229,255,0.08)",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=years, y=results["consumption"],
        name="Consumption",
        line=dict(color=COLORS["consumption"], width=2),
        fill="tozeroy", fillcolor="rgba(0,201,167,0.08)",
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=years, y=results["welfare"],
        name="Welfare",
        line=dict(color=COLORS["welfare"], width=2),
        fill="tozeroy", fillcolor="rgba(255,209,102,0.08)",
    ), row=3, col=1)

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"Macroeconomic Projections  ·  {results['country']}",
                   font=dict(color=TEXT, size=13)),
        height=520,
    )

    fig.update_xaxes(**_axis("Year"),   row=3, col=1)
    fig.update_xaxes(**_axis(),         row=1, col=1)
    fig.update_xaxes(**_axis(),         row=2, col=1)
    fig.update_yaxes(**_axis("Value"),  row=1, col=1)
    fig.update_yaxes(**_axis("Value"),  row=2, col=1)
    fig.update_yaxes(**_axis("Utils"),  row=3, col=1)

    return _to_html(fig)


def build_clews_chart(results: dict) -> str:
    years = results["years"]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=years, y=results["renewable_share"],
        name="Renewable Share (%)",
        line=dict(color=COLORS["renewable"], width=2),
        fill="tozeroy", fillcolor="rgba(6,214,160,0.10)",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=years, y=results["co2_emissions"],
        name="CO₂ Emissions (index)",
        line=dict(color=COLORS["co2"], width=2, dash="dot"),
    ), secondary_y=True)

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"CLEWS Energy & Emissions  ·  {results['country']}",
                   font=dict(color=TEXT, size=13)),
        height=400,
    )

    fig.update_xaxes(**_axis("Year"))
    fig.update_yaxes(**_axis("Renewable Share (%)"), secondary_y=False)
    fig.update_yaxes(**_axis("CO₂ (index)"),         secondary_y=True)

    return _to_html(fig)


def build_scores_chart(results: dict) -> str:
    scores = results["scores"]

    color_map = {
        "GDP Growth (avg %)":   "#00e5ff",
        "CO₂ Reduction (%)":    "#06d6a0",
        "Welfare Gain (%)":     "#ffd166",
        "Renewable Target Met": "#ff6b35",
    }

    labels, values, colors_list = [], [], []
    for k, v in scores.items():
        labels.append(k)
        values.append(100 if v == "Yes" else (0 if v == "No" else v))
        colors_list.append(color_map.get(k, "#00e5ff"))

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(color=colors_list, opacity=0.85),
        text=[str(v) for v in scores.values()],
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
    ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="Policy Impact Scores",
                   font=dict(color=TEXT, size=13)),
        height=300,
        xaxis=_axis("Score"),
        yaxis=_axis(),
    )

    return _to_html(fig)
