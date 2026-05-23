"""UI components: wave SVG, CSS, and the app layout."""

from dash import dcc, html


# ─── Water wave SVG animation ───────────────────────────────────────────────
def wave_svg(color1="rgba(59,130,246,0.5)", color2="rgba(14,165,233,0.4)"):
    """Inline SVG with CSS keyframe animation for a subtle wave."""
    return f"""<div style="position:fixed;bottom:0;left:0;width:100%;height:120px;background:linear-gradient(180deg,{color1},{color2});z-index:-1;pointer-events:none;"></div>"""


# ─── Dash HTML template ─────────────────────────────────────────────────────
APP_INDEX_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    __DASH_METAS__
    <title>__DASH_TITLE__</title>
    __DASH_FAVICON__
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    {%css%}
</head>
<body>
    <div style="position: relative;">
        <!-- Animated wave background -->
        __DASH_WAVE_SVG__
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </div>
</body>
</html>"""


# ─── Layout helper ──────────────────────────────────────────────────────────
def build_layout():
    """Build the complete Dash app layout."""
    return html.Div(
        [
            # ─── Header ─────────────────────────────────────────────────────
            html.Div(
                [
                    html.H1("Fäbu's App", className="header-title"),
                    html.P(
                        html.Span(className="live-dot"),
                        " Live – Aare & Reuss Wasser-Monitoring",
                        className="subtitle",
                    ),
                ],
                className="header-container",
            ),

            # ─── Latest measurements dashboard ──────────────────────────────
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(className="section-icon", children="💧"),
                            html.H2("Aktuelle Messwerte"),
                        ],
                        className="section-header",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    # River labels row
                                    html.Div(
                                        [
                                            html.Div(className="river-label", children=[
                                                html.Span(className="river-icon", children="🏔️"),
                                                "Aare",
                                            ]),
                                            html.Div(className="river-label", children=[
                                                html.Span(className="river-icon", children="🏞️"),
                                                "Reuss",
                                            ]),
                                        ],
                                        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px", "marginBottom": "12px"},
                                    ),
                                    # Row 1: Temperature
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.P("🌡️ Temperatur", className="card-title"),
                                                    html.Div(id="aare-temp-value", className="card-value"),
                                                    html.Div(id="aare-temp-time", className="card-time"),
                                                ],
                                                className="measurement-card temp",
                                            ),
                                            html.Div(
                                                [
                                                    html.P("🌡️ Temperatur", className="card-title"),
                                                    html.Div(id="reuss-temp-value", className="card-value"),
                                                    html.Div(id="reuss-temp-time", className="card-time"),
                                                ],
                                                className="measurement-card temp",
                                            ),
                                        ],
                                        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px", "marginBottom": "10px"},
                                    ),
                                    # Row 2: Flow
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.P("🌊 Abfluss", className="card-title"),
                                                    html.Div(id="aare-flow-value", className="card-value"),
                                                    html.Div(id="aare-flow-time", className="card-time"),
                                                ],
                                                className="measurement-card flow",
                                            ),
                                            html.Div(
                                                [
                                                    html.P("🌊 Abfluss", className="card-title"),
                                                    html.Div(id="reuss-flow-value", className="card-value"),
                                                    html.Div(id="reuss-flow-time", className="card-time"),
                                                ],
                                                className="measurement-card flow",
                                            ),
                                        ],
                                        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px", "marginBottom": "10px"},
                                    ),
                                    # Row 3: Water level
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.P("📏 Wasserstand", className="card-title"),
                                                    html.Div(id="aare-level-value", className="card-value"),
                                                    html.Div(id="aare-level-time", className="card-time"),
                                                ],
                                                className="measurement-card level",
                                            ),
                                            html.Div(
                                                [
                                                    html.P("📏 Wasserstand", className="card-title"),
                                                    html.Div(id="reuss-level-value", className="card-value"),
                                                    html.Div(id="reuss-level-time", className="card-time"),
                                                ],
                                                className="measurement-card level",
                                            ),
                                        ],
                                        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "8px"},
                                    ),
                                ],
                                className="glass-card",
                            ),
                        ],
                        className="measurement-grid",
                    ),
                    html.Div(id="last-updated", className="last-updated"),
                ],
                style={"padding": "0 20px"},
            ),

            # ─── Combined plots ─────────────────────────────────────────────
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(className="section-icon", children="🔗"),
                            html.H2("Vergleich: Aare & Reuss"),
                        ],
                        className="section-header",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(className="graph-title", children=[
                                        html.Span(className="icon", children="🌡️"),
                                        "Temperatur im Vergleich (7 Tage)",
                                    ]),
                                    dcc.Graph(
                                        id="combined-temp-graph",
                                        config={"displayModeBar": False, "responsive": True},
                                        style={"height": "40vh"},
                                    ),
                                ],
                                className="graph-container",
                            ),
                            html.Div(
                                [
                                    html.Div(className="graph-title", children=[
                                        html.Span(className="icon", children="🌊"),
                                        "Abfluss & Wasserstand im Vergleich (7 Tage)",
                                    ]),
                                    dcc.Graph(
                                        id="combined-flow-graph",
                                        config={"displayModeBar": False, "responsive": True},
                                        style={"height": "40vh"},
                                    ),
                                ],
                                className="graph-container",
                            ),
                        ],
                        style={"display": "grid", "gridTemplateColumns": "1fr", "gap": "20px"},
                        className="graph-section",
                    ),
                ],
                style={"padding": "0 20px"},
            ),

            # ─── Aare graphs ────────────────────────────────────────────────
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(className="section-icon", children="📈"),
                            html.H2("Aare"),
                        ],
                        className="section-header",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(className="graph-title", children=[
                                        html.Span(className="icon", children="🌡️"),
                                        "Temperatur (7 Tage)",
                                    ]),
                                    dcc.Graph(
                                        id="aare-temp-graph",
                                        config={"displayModeBar": False, "responsive": True},
                                        style={"height": "40vh"},
                                    ),
                                ],
                                className="graph-container",
                            ),
                            html.Div(
                                [
                                    html.Div(className="graph-title", children=[
                                        html.Span(className="icon", children="🌊"),
                                        "Abfluss & Wasserstand (7 Tage)",
                                    ]),
                                    dcc.Graph(
                                        id="aare-flow-graph",
                                        config={"displayModeBar": False, "responsive": True},
                                        style={"height": "40vh"},
                                    ),
                                ],
                                className="graph-container",
                            ),
                        ],
                        style={"display": "grid", "gridTemplateColumns": "1fr", "gap": "20px"},
                        className="graph-section",
                    ),
                ],
                style={"padding": "0 20px"},
            ),

            # ─── Reuss graphs ───────────────────────────────────────────────
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(className="section-icon", children="📈"),
                            html.H2("Reuss"),
                        ],
                        className="section-header",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(className="graph-title", children=[
                                        html.Span(className="icon", children="🌡️"),
                                        "Temperatur (7 Tage)",
                                    ]),
                                    dcc.Graph(
                                        id="reuss-temp-graph",
                                        config={"displayModeBar": False, "responsive": True},
                                        style={"height": "40vh"},
                                    ),
                                ],
                                className="graph-container",
                            ),
                            html.Div(
                                [
                                    html.Div(className="graph-title", children=[
                                        html.Span(className="icon", children="🌊"),
                                        "Abfluss & Wasserstand (7 Tage)",
                                    ]),
                                    dcc.Graph(
                                        id="reuss-flow-graph",
                                        config={"displayModeBar": False, "responsive": True},
                                        style={"height": "40vh"},
                                    ),
                                ],
                                className="graph-container",
                            ),
                        ],
                        style={"display": "grid", "gridTemplateColumns": "1fr", "gap": "20px"},
                        className="graph-section",
                    ),
                ],
                style={"padding": "0 20px"},
            ),

            dcc.Interval(
                id="interval-refresh", interval=10 * 60 * 1000, n_intervals=0
            ),  # 10 min

            html.Footer(
                "Made with 💧 for Swiss waters • Daten von hydrodaten.admin.ch",
                className="footer",
            ),
        ],
    )
