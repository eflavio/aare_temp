"""Reusable UI component builders."""

from dash import dcc, html

# ── Measurement card ──────────────────────────────────────────────────────

_METRICS = [
    ("Temperature", "temp", "🌡️", "temp-value", "temp-time"),
    ("Flow", "flow", "🌊", "flow-value", "flow-time"),
    ("Water Level", "level", "📏", "level-value", "level-time"),
]


def _make_metric_card(title, icon, metric_key, value_id, time_id):
    """Build a single metric card."""
    return html.Div(
        [
            html.P(f"{icon} {title}", className="card-title"),
            html.Div(id=value_id, className="card-value"),
            html.Div(id=time_id, className="card-time"),
        ],
        className=f"measurement-card {metric_key}",
    )


def measurement_card(prefix):
    """Build all metric cards for one river (e.g. 'aare' or 'reuss')."""
    rows = []
    for title, cls, icon, value_id, time_id in _METRICS:
        rows.append(_make_metric_card(
            title, icon, cls,
            f"{prefix}-{value_id}",
            f"{prefix}-{time_id}",
        ))
    return html.Div(
        [html.Div(row, style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px"})
         for row in rows],
        className="cards-row",
    )


def measurement_header():
    """River label header for the comparison card."""
    return html.Div(
        [
            html.Div(
                [html.Span(className="river-icon", children="🏔️"), "Aare"],
                className="river-label",
            ),
            html.Div(
                [html.Span(className="river-icon", children="🏞️"), "Reuss"],
                className="river-label",
            ),
        ],
        className="river-headers",
    )


def section_header(icon, title):
    """Section header with icon."""
    return html.Div(
        [
            html.Span(className="section-icon", children=icon),
            html.H2(title),
        ],
        className="section-header",
    )


def graph_card(title, icon, graph_id, height="40vh"):
    """A graph wrapped in a styled container."""
    return html.Div(
        [
            html.Div(
                className="graph-title",
                children=[html.Span(className="icon", children=icon), title],
            ),
            dcc.Graph(
                id=graph_id,
                config={"displayModeBar": False, "responsive": True},
                style={"height": height},
            ),
        ],
        className="graph-container",
    )


def build_layout():
    """Build the complete app layout."""
    return html.Div(
        [
            # ── Header ────────────────────────────────────────────────
            html.Div(
                [
                    html.H1("Fäbu's App", className="header-title"),
                    html.P(
                        [html.Span(className="live-dot"),
                         " Live – Aare & Reuss Wasser-Monitoring"],
                        className="subtitle",
                    ),
                ],
                className="header-container",
            ),

            # ── Latest measurements ───────────────────────────────────
            html.Div(
                [
                    section_header("💧", "Aktuelle Messwerte"),
                    html.Div(
                        [
                            measurement_header(),
                            html.Div(
                                [
                                    measurement_card("aare"),
                                    measurement_card("reuss"),
                                ],
                                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px"},
                                className="cards-row",
                            ),
                        ],
                        className="glass-card",
                    ),
                ],
                className="measurement-grid",
            ),

            html.Div(id="last-updated", className="last-updated"),

            # ── Combined comparison ───────────────────────────────────
            html.Div(
                [
                    section_header("🔗", "Vergleich: Aare & Reuss"),
                    html.Div(
                        [
                            graph_card(
                                "Temperatur im Vergleich (7 Tage)", "🌡️",
                                "combined-temp-graph",
                            ),
                            graph_card(
                                "Abfluss & Wasserstand im Vergleich (7 Tage)", "🌊",
                                "combined-flow-graph",
                            ),
                        ],
                        className="graph-section",
                    ),
                ],
                style={"padding": "0 20px"},
            ),

            # ── Aare detail ───────────────────────────────────────────
            html.Div(
                [
                    section_header("📈", "Aare"),
                    html.Div(
                        [
                            graph_card("Temperatur (7 Tage)", "🌡️", "aare-temp-graph"),
                            graph_card("Abfluss & Wasserstand (7 Tage)", "🌊", "aare-flow-graph"),
                        ],
                        className="graph-section",
                    ),
                ],
                style={"padding": "0 20px"},
            ),

            # ── Reuss detail ──────────────────────────────────────────
            html.Div(
                [
                    section_header("📈", "Reuss"),
                    html.Div(
                        [
                            graph_card("Temperatur (7 Tage)", "🌡️", "reuss-temp-graph"),
                            graph_card("Abfluss & Wasserstand (7 Tage)", "🌊", "reuss-flow-graph"),
                        ],
                        className="graph-section",
                    ),
                ],
                style={"padding": "0 20px"},
            ),

            # ── Refresh timer ─────────────────────────────────────────
            dcc.Interval(
                id="interval-refresh",
                interval=10 * 60 * 1000,
                n_intervals=0,
            ),

            # ── Footer ────────────────────────────────────────────────
            html.Footer(
                "Made with 💧 for Swiss waters • Daten von hydrodaten.admin.ch",
                className="footer",
            ),
        ],
    )
