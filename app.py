import dash
from dash import dcc, html, Output, Input, callback_context
import requests
import datetime


# ─── Helper: load plot data from hydrodaten.admin.ch ────────────────────────
def load_plot(station_id="2135", title="Aare", plot_type="temperature"):
    """
    Load plot data from hydrodaten.admin.ch
    plot_type can be 'temperature' or 'flow' (for Abfluss und Wasserstand)
    Returns:
        tuple: (plot_data, latest_values)
               where latest_values is a dict with keys 'value', 'unit', 'time'
    """
    if plot_type == "temperature":
        url = f"https://www.hydrodaten.admin.ch/plots/temperature_7days/{station_id}_temperature_7days_de.json"
    else:  # flow and water level
        url = f"https://www.hydrodaten.admin.ch/plots/p_q_7days/{station_id}_p_q_7days_de.json"

    response = requests.get(url)
    data = response.json()

    # Add hover info for all data series in the plot
    for series in data["plot"]["data"]:
        if "hoverinfo" in series:
            series["hoverinfo"] = "x+y+name"

    # Extract latest measurements
    latest_values = {}
    if plot_type == "temperature":
        # Get the latest temperature value
        if data["plot"]["data"] and len(data["plot"]["data"]) > 0:
            temp_data = data["plot"]["data"][0]
            if (
                "x" in temp_data
                and "y" in temp_data
                and len(temp_data["x"]) > 0
                and len(temp_data["y"]) > 0
            ):
                latest_values["value"] = temp_data["y"][-1]
                latest_values["time"] = temp_data["x"][-1]
                latest_values["unit"] = "°C"
    else:
        # For flow plots, there are usually multiple data series (flow and water level)
        values = {}
        for series in data["plot"]["data"]:
            if (
                "x" in series
                and "y" in series
                and len(series["x"]) > 0
                and len(series["y"]) > 0
            ):
                if "name" in series:
                    name = series["name"]
                    if "Abfluss" in name:
                        values["flow"] = {
                            "value": series["y"][-1],
                            "time": series["x"][-1],
                            "unit": "m³/s",
                        }
                    elif "Wasserstand" in name or "Pegel" in name:
                        values["level"] = {
                            "value": series["y"][-1],
                            "time": series["x"][-1],
                            "unit": "m",
                        }
        latest_values = values

    return data["plot"], latest_values


# ─── Water wave SVG animation ───────────────────────────────────────────────
def wave_svg(color1="rgba(59,130,246,0.08)", color2="rgba(14,165,233,0.06)"):
    """Inline SVG with CSS keyframe animation for a subtle wave."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 120" preserveAspectRatio="none"
        style="position:absolute;bottom:0;left:0;width:100%;height:60px;pointer-events:none;opacity:0.7;">
        <defs>
            <linearGradient id="wg" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="{color1}" />
                <stop offset="100%" stop-color="{color2}" />
            </linearGradient>
        </defs>
        <path fill="url(#wg)" d="M0,64 C360,120 720,0 1080,64 C1260,96 1380,80 1440,64 L1440,120 L0,120 Z">
            <animate attributeName="d"
                values="M0,64 C360,120 720,0 1080,64 C1260,96 1380,80 1440,64 L1440,120 L0,120 Z;
                        M0,80 C320,32 640,112 960,48 C1200,8 1380,72 1440,80 L1440,120 L0,120 Z;
                        M0,64 C360,120 720,0 1080,64 C1260,96 1380,80 1440,64 L1440,120 L0,120 Z"
                dur="8s" repeatCount="indefinite"/>
        </path>
        <path fill="url(#wg)" opacity="0.5"
            d="M0,80 C240,32 480,112 720,64 C960,16 1200,96 1440,48 L1440,120 L0,120 Z">
            <animate attributeName="d"
                values="M0,80 C240,32 480,112 720,64 C960,16 1200,96 1440,48 L1440,120 L0,120 Z;
                        M0,48 C360,96 720,16 1080,80 C1260,112 1380,32 1440,48 L1440,120 L0,120 Z;
                        M0,80 C240,32 480,112 720,64 C960,16 1200,96 1440,48 L1440,120 L0,120 Z"
                dur="6s" repeatCount="indefinite"/>
        </path>
    </svg>"""


# ─── Build combined plot from two river datasets ───────────────────────────
def build_combined_plot(aare_data, reuss_data, aare_label, reuss_label, title_text):
    """Merge two river datasets into a single combined Plotly figure."""
    combined = {"data": [], "layout": {"title": {"text": title_text}}}

    color_map = {
        "Aare": "#3b82f6",
        "Reuss": "#06b6d4",
    }

    # Copy xaxis/yaxis config from source so spike lines etc. work
    source = aare_data.get("layout", {})
    combined["layout"]["xaxis"] = dict(source.get("xaxis", {}))
    combined["layout"]["yaxis"] = dict(source.get("yaxis", {}))

    for label, data in [(aare_label, aare_data), (reuss_label, reuss_data)]:
        for series in data.get("data", []):
            if "x" not in series or "y" not in series:
                continue
            new_series = {
                "x": series["x"],
                "y": series["y"],
                "name": f"{label} – {series.get('name', '')}",
                "line": {"color": color_map.get(label, "#94a3b8"), "width": 2.5},
                "marker": {"size": 5},
                "hoverinfo": "x+y+name",
            }
            combined["data"].append(new_series)

    return combined


# ─── Dark-themed Plotly layout helper ───────────────────────────────────────
def apply_dark_theme(plot, title_text):
    """Apply a polished dark theme to a Plotly figure."""
    plot["layout"].update(
        title={
            "text": title_text,
            "font": {"size": 16, "color": "#f1f5f9", "family": "Inter"},
            "x": 0.5,
            "xanchor": "center",
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif", "color": "#94a3b8", "size": 12},
        margin={"l": 50, "r": 20, "t": 50, "b": 40},
        legend={
            "font": {"size": 11, "color": "#94a3b8"},
            "bgcolor": "rgba(15,23,42,0.6)",
            "bordercolor": "rgba(148,163,184,0.15)",
            "borderwidth": 1,
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.18,
            "yanchor": "top",
        },
        hoverlabel={
            "bgcolor": "rgba(15,23,42,0.95)",
            "bordercolor": "rgba(6,182,212,0.5)",
            "font": {"size": 13, "color": "#f1f5f9", "family": "Inter"},
        },
        hovermode="x unified",
        hoverdistance=50,
        spikedistance=-1,
        xaxis={
            **plot["layout"].get("xaxis", {}),
            "gridcolor": "rgba(148,163,184,0.1)",
            "zerolinecolor": "rgba(148,163,184,0.15)",
            "tickfont": {"size": 11, "color": "#64748b"},
            "tickformat": "%d.%m.%Y %H:%M",
            "spikemode": "across",
            "spikesnap": "data",
            "spikedash": "dot",
            "spikethickness": 1,
        },
        yaxis={
            **plot["layout"].get("yaxis", {}),
            "gridcolor": "rgba(148,163,184,0.1)",
            "zerolinecolor": "rgba(148,163,184,0.15)",
            "tickfont": {"size": 11, "color": "#64748b"},
            "spikemode": "across",
            "spikesnap": "data",
            "spikedash": "dot",
            "spikethickness": 1,
        },
    )

    # Darken line markers
    for i, series in enumerate(plot.get("data", [])):
        if "line" in series:
            series["line"].update(width=2.5)
        if "marker" in series:
            series["marker"].update(size=5)

    return plot


# ─── Dash app ────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="Fäbu's App – Aare & Reuss Monitor")
server = app.server

# Custom HTML with fonts, CSS variables, and dark theme
app.index_string = """<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.85);
            --bg-card-hover: rgba(30, 41, 59, 0.95);
            --border-color: rgba(148, 163, 184, 0.15);
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-blue: #3b82f6;
            --accent-cyan: #06b6d4;
            --accent-teal: #14b8a6;
            --accent-indigo: #6366f1;
            --accent-sky: #0ea5e9;
            --glow-blue: rgba(59, 130, 246, 0.4);
            --glow-cyan: rgba(6, 182, 212, 0.3);
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.3), 0 2px 4px -2px rgba(0,0,0,0.2);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.4), 0 4px 6px -4px rgba(0,0,0,0.3);
            --shadow-glow: 0 0 20px var(--glow-blue), 0 0 40px rgba(6,182,212,0.15);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 20px;
        }

        * { box-sizing: border-box; }

        html, body {
            margin: 0; padding: 0;
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Animated gradient background */
        body::before {
            content: '';
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background:
                radial-gradient(ellipse at 20% 20%, rgba(59,130,246,0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(6,182,212,0.06) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(99,102,241,0.04) 0%, transparent 60%);
            z-index: -1;
            animation: bgShift 20s ease-in-out infinite alternate;
        }
        @keyframes bgShift {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-primary); }
        ::-webkit-scrollbar-thumb { background: var(--text-muted); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); }

        /* Header */
        .header-container {
            position: relative;
            text-align: center;
            padding: 32px 20px 48px;
            overflow: hidden;
        }
        .header-title {
            font-size: 2.4rem;
            font-weight: 700;
            margin: 0 0 8px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan), var(--accent-teal));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.5px;
        }
        .subtitle {
            color: var(--text-secondary);
            font-size: 0.95rem;
            font-weight: 400;
            margin: 0;
        }

        /* Live indicator */
        .live-dot {
            display: inline-block;
            width: 8px; height: 8px;
            background: #22c55e;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 2s ease-in-out infinite;
            vertical-align: middle;
        }
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(34,197,94,0.6); }
            50% { box-shadow: 0 0 0 6px rgba(34,197,94,0); }
        }

        /* Cards */
        .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 16px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-md);
        }
        .glass-card:hover {
            background: var(--bg-card-hover);
            box-shadow: var(--shadow-lg);
            border-color: rgba(148, 163, 184, 0.25);
            transform: translateY(-2px);
        }

        /* Section headers */
        .section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 14px;
        }
        .section-header h2 {
            font-size: 1.2rem;
            font-weight: 600;
            margin: 0;
            color: var(--text-primary);
        }
        .section-icon {
            font-size: 1.3rem;
        }

        /* Measurement cards */
        .measurement-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 10px 8px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-sm);
            position: relative;
            overflow: hidden;
        }
        .measurement-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            border-radius: var(--radius-md) var(--radius-md) 0 0;
        }
        .measurement-card.temp::before { background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)); }
        .measurement-card.flow::before { background: linear-gradient(90deg, var(--accent-teal), var(--accent-sky)); }
        .measurement-card.level::before { background: linear-gradient(90deg, var(--accent-indigo), var(--accent-blue)); }
        .measurement-card:hover {
            background: var(--bg-card-hover);
            box-shadow: var(--shadow-md);
            transform: translateY(-3px);
        }
        .measurement-card .card-title {
            font-size: 0.65rem;
            font-weight: 500;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0 0 4px;
        }
        .measurement-card .card-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.4rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0 0 2px;
            line-height: 1.2;
        }
        .measurement-card .card-unit {
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-weight: 400;
        }
        .measurement-card .card-time {
            font-size: 0.6rem;
            color: var(--text-muted);
            margin-top: 4px;
        }

        /* River label */
        .river-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0;
            display: flex;
            align-items: center;
            gap: 6px;
            justify-content: center;
        }
        .river-label .river-icon {
            font-size: 1rem;
        }

        /* Measurement grid */
        .measurement-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 0;
            margin-bottom: 16px;
        }
        /* ── Mobile responsive ─────────────────────────────────────────────── */
        @media (max-width: 768px) {
            .measurement-grid { grid-template-columns: 1fr; }
            .header-container { padding: 20px 12px 40px; }
            .header-title { font-size: 1.6rem; }
            .subtitle { font-size: 0.8rem; }
            .glass-card { padding: 12px; }
            .river-label { font-size: 0.9rem; margin-bottom: 8px; }
            .river-label .river-icon { font-size: 1rem; }
            .measurement-card { padding: 8px 6px; }
            .measurement-card .card-title { font-size: 0.55rem; margin-bottom: 3px; }
            .measurement-card .card-value { font-size: 1.1rem; }
            .measurement-card .card-unit { font-size: 0.65rem; }
            .measurement-card .card-time { font-size: 0.55rem; margin-top: 3px; }
            .section-header { margin-bottom: 12px; }
            .section-header h2 { font-size: 1.1rem; }
            .section-icon { font-size: 1.2rem; }
            .graph-container { padding: 12px; }
            .graph-title { font-size: 0.85rem; margin-bottom: 8px; }
            .graph-title .icon { font-size: 0.95rem; }
        }
        @media (max-width: 400px) {
            .measurement-card .card-value { font-size: 1rem; }
            .measurement-card .card-title { font-size: 0.55rem; }
            .header-title { font-size: 1.3rem; }
        }

        /* Last updated */
        .last-updated {
            text-align: right;
            font-size: 0.8rem;
            color: var(--text-muted);
            padding: 8px 0;
        }

        /* Graph container */
        .graph-section {
            margin-bottom: 24px;
        }
        .graph-container {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 20px;
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
        }
        .graph-container:hover {
            box-shadow: var(--shadow-lg);
        }
        .graph-title {
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-secondary);
            margin: 0 0 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .graph-title .icon {
            font-size: 1.1rem;
        }

        /* Loading spinner */
        .loading-overlay {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 200px;
        }
        .spinner {
            width: 40px; height: 40px;
            border: 3px solid var(--border-color);
            border-top-color: var(--accent-cyan);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* Footer */
        .footer {
            text-align: center;
            padding: 20px;
            color: var(--text-muted);
            font-size: 0.75rem;
        }

        /* Dash graph overrides */
        .js-plotly-plot .plotly .modebar {
            top: 8px !important;
            right: 8px !important;
        }
        .js-plotly-plot .plotly .modebar-btn {
            background-color: transparent !important;
        }
        .js-plotly-plot .plotly .modebar-btn svg {
            fill: var(--text-muted) !important;
        }
        .js-plotly-plot .plotly .modebar-btn:hover svg {
            fill: var(--text-primary) !important;
        }
    </style>
</head>
<body>
    <div style="position: relative;">
        <!-- Animated wave background -->
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 120" preserveAspectRatio="none"
            style="position:absolute;bottom:0;left:0;width:100%;height:60px;pointer-events:none;opacity:0.7;z-index:-1;">
            <defs>
                <linearGradient id="wg" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="rgba(59,130,246,0.08)" />
                    <stop offset="100%" stop-color="rgba(14,165,233,0.06)" />
                </linearGradient>
            </defs>
            <path fill="url(#wg)" d="M0,64 C360,120 720,0 1080,64 C1260,96 1380,80 1440,64 L1440,120 L0,120 Z">
                <animate attributeName="d"
                    values="M0,64 C360,120 720,0 1080,64 C1260,96 1380,80 1440,64 L1440,120 L0,120 Z;
                            M0,80 C320,32 640,112 960,48 C1200,8 1380,72 1440,80 L1440,120 L0,120 Z;
                            M0,64 C360,120 720,0 1080,64 C1260,96 1380,80 1440,64 L1440,120 L0,120 Z"
                    dur="8s" repeatCount="indefinite"/>
            </path>
            <path fill="url(#wg)" opacity="0.5"
                d="M0,80 C240,32 480,112 720,64 C960,16 1200,96 1440,48 L1440,120 L0,120 Z">
                <animate attributeName="d"
                    values="M0,80 C240,32 480,112 720,64 C960,16 1200,96 1440,48 L1440,120 L0,120 Z;
                            M0,48 C360,96 720,16 1080,80 C1260,112 1380,32 1440,48 L1440,120 L0,120 Z;
                            M0,80 C240,32 480,112 720,64 C960,16 1200,96 1440,48 L1440,120 L0,120 Z"
                    dur="6s" repeatCount="indefinite"/>
            </path>
        </svg>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </div>
</body>
</html>"""

app.layout = html.Div(
    [
        # ─── Header ─────────────────────────────────────────────────────────────
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

        # ─── Latest measurements dashboard ──────────────────────────────────────
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
                        # ── Single combined card ─────────────────────
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
                                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px"},
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

        # ─── Combined plots ─────────────────────────────────────────────────────
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

        # ─── Aare graphs ────────────────────────────────────────────────────────
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

        # ─── Reuss graphs ───────────────────────────────────────────────────────
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


@app.callback(
    [
        # Graph figures
        Output("combined-temp-graph", "figure"),
        Output("combined-flow-graph", "figure"),
        Output("aare-temp-graph", "figure"),
        Output("aare-flow-graph", "figure"),
        Output("reuss-temp-graph", "figure"),
        Output("reuss-flow-graph", "figure"),
        # Latest measurements for display
        Output("aare-temp-value", "children"),
        Output("aare-flow-value", "children"),
        Output("aare-level-value", "children"),
        Output("reuss-temp-value", "children"),
        Output("reuss-flow-value", "children"),
        Output("reuss-level-value", "children"),
        # Time stamps for measurement cards
        Output("aare-temp-time", "children"),
        Output("aare-flow-time", "children"),
        Output("aare-level-time", "children"),
        Output("reuss-temp-time", "children"),
        Output("reuss-flow-time", "children"),
        Output("reuss-level-time", "children"),
        # Last updated timestamp
        Output("last-updated", "children"),
    ],
    Input("interval-refresh", "n_intervals"),
)
def update_plots(n):
    # Get temperature plots and latest values
    aare_temp_plot, aare_temp_latest = load_plot(
        station_id="2135", title="Temperatur", plot_type="temperature"
    )
    reuss_temp_plot, reuss_temp_latest = load_plot(
        station_id="2152", title="Temperatur", plot_type="temperature"
    )

    # Get flow and water level plots and latest values
    aare_flow_plot, aare_flow_latest = load_plot(
        station_id="2135", title="Abfluss & Wasserstand", plot_type="flow"
    )
    reuss_flow_plot, reuss_flow_latest = load_plot(
        station_id="2152", title="Abfluss & Wasserstand", plot_type="flow"
    )

    # Build combined comparison plots
    combined_temp = build_combined_plot(
        aare_temp_plot, reuss_temp_plot, "Aare", "Reuss", "Temperatur – Aare & Reuss"
    )
    combined_flow = build_combined_plot(
        aare_flow_plot, reuss_flow_plot, "Aare", "Reuss", "Abfluss & Wasserstand – Aare & Reuss"
    )

    # Apply modern dark theme to all plots
    for plot, title in [
        (combined_temp, "Temperatur – Aare & Reuss"),
        (combined_flow, "Abfluss & Wasserstand – Aare & Reuss"),
        (aare_temp_plot, "Temperatur – Aare"),
        (aare_flow_plot, "Abfluss & Wasserstand – Aare"),
        (reuss_temp_plot, "Temperatur – Reuss"),
        (reuss_flow_plot, "Abfluss & Wasserstand – Reuss"),
    ]:
        apply_dark_theme(plot, title)

    # Format latest measurement values for display
    current_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    def fmt_time(raw_time):
        """Format ISO-ish time to readable Swiss format."""
        if not raw_time:
            return ""
        try:
            dt = datetime.datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            return dt.strftime("%d.%m. %H:%M")
        except (ValueError, TypeError):
            return raw_time

    # Temperature values
    aare_temp_display = (
        f"{aare_temp_latest.get('value', 'N/A'):.1f} {aare_temp_latest.get('unit', '°C')}"
        if "value" in aare_temp_latest
        else "N/A"
    )
    reuss_temp_display = (
        f"{reuss_temp_latest.get('value', 'N/A'):.1f} {reuss_temp_latest.get('unit', '°C')}"
        if "value" in reuss_temp_latest
        else "N/A"
    )

    # Flow values
    aare_flow_display = (
        f"{aare_flow_latest.get('flow', {}).get('value', 'N/A'):.1f} {aare_flow_latest.get('flow', {}).get('unit', 'm³/s')}"
        if "flow" in aare_flow_latest
        else "N/A"
    )
    reuss_flow_display = (
        f"{reuss_flow_latest.get('flow', {}).get('value', 'N/A'):.1f} {reuss_flow_latest.get('flow', {}).get('unit', 'm³/s')}"
        if "flow" in reuss_flow_latest
        else "N/A"
    )

    # Water level values
    aare_level_display = (
        f"{aare_flow_latest.get('level', {}).get('value', 'N/A'):.2f} {aare_flow_latest.get('level', {}).get('unit', 'm')}"
        if "level" in aare_flow_latest
        else "N/A"
    )
    reuss_level_display = (
        f"{reuss_flow_latest.get('level', {}).get('value', 'N/A'):.2f} {reuss_flow_latest.get('level', {}).get('unit', 'm')}"
        if "level" in reuss_flow_latest
        else "N/A"
    )

    # Last updated message
    last_updated = f"Letzte Aktualisierung: {current_time}"

    # Time stamps for cards
    aare_temp_time = fmt_time(aare_temp_latest.get("time"))
    aare_flow_time = fmt_time(aare_flow_latest.get("flow", {}).get("time"))
    aare_level_time = fmt_time(aare_flow_latest.get("level", {}).get("time"))
    reuss_temp_time = fmt_time(reuss_temp_latest.get("time"))
    reuss_flow_time = fmt_time(reuss_flow_latest.get("flow", {}).get("time"))
    reuss_level_time = fmt_time(reuss_flow_latest.get("level", {}).get("time"))

    return (
        combined_temp,
        combined_flow,
        aare_temp_plot,
        aare_flow_plot,
        reuss_temp_plot,
        reuss_flow_plot,
        aare_temp_display,
        aare_flow_display,
        aare_level_display,
        reuss_temp_display,
        reuss_flow_display,
        reuss_level_display,
        aare_temp_time,
        aare_flow_time,
        aare_level_time,
        reuss_temp_time,
        reuss_flow_time,
        reuss_level_time,
        last_updated,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
