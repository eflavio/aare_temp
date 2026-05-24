"""Plot helpers using plotly.graph_objects."""

import plotly.graph_objects as go

RIVER_COLORS = {"Aare": "#3b82f6", "Reuss": "#06b6d4"}


def make_trace(data, label):
    """Create a Plotly trace from raw data dict."""
    return go.Scatter(
        x=data["x"],
        y=data["y"],
        name=f"{label} – {data.get('name', '')}",
        mode="lines",
        line=dict(color=RIVER_COLORS.get(label, "#94a3b8"), width=2.5),
        marker=dict(size=5),
        hovertemplate="%{y:.2f}<br>%{x|%d.%m. %H:%M}<extra>%{fullData.name}</extra>",
        hoverinfo="skip",
    )


def build_single_plot(data, label):
    """Build a Plotly figure from raw plot data."""
    traces = [make_trace(d, label) for d in data.get("data", [])]
    fig = go.Figure(data=traces)
    _apply_theme(fig)
    return fig


def build_combined_plot(data_aare, data_reuss):
    """Merge two river datasets into a single figure."""
    traces = []
    for data, label in [(data_aare, "Aare"), (data_reuss, "Reuss")]:
        traces.extend(make_trace(d, label) for d in data.get("data", []))

    fig = go.Figure(data=traces)

    # Shared y-range so neither river is squashed
    all_y = [v for d in [data_aare, data_reuss] for t in d.get("data", []) for v in t.get("y", [])]
    if all_y:
        y_min, y_max = min(all_y), max(all_y)
        span = y_max - y_min
        fig.update_yaxes(range=[y_min - span * 0.1, y_max + span * 0.1])

    _apply_theme(fig)
    return fig


# ── Dark theme layout config ──────────────────────────────────────────────

_DARK_LAYOUT = dict(
    title=dict(text="", font=dict(size=16, family="Inter")),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94a3b8"),
    margin=dict(l=50, r=20, t=50, b=40),
    legend=dict(
        font=dict(size=11, color="#94a3b8"),
        bgcolor="rgba(15,23,42,0.6)",
        bordercolor="rgba(148,163,184,0.15)",
        borderwidth=1,
        orientation="h",
        x=0.5, xanchor="center",
        y=-0.18, yanchor="top",
    ),
    hovermode="x unified",
    hoverdistance=50,
    spikedistance=-1,
    xaxis=dict(
        gridcolor="rgba(148,163,184,0.1)",
        zerolinecolor="rgba(148,163,184,0.15)",
        tickfont=dict(size=11, color="#64748b"),
        tickformat="%d.%m.%Y %H:%M",
        spikemode="across", spikesnap="data",
        spikedash="dot", spikethickness=1,
    ),
    yaxis=dict(
        gridcolor="rgba(148,163,184,0.1)",
        zerolinecolor="rgba(148,163,184,0.15)",
        tickfont=dict(size=11, color="#64748b"),
        spikemode="across", spikesnap="data",
        spikedash="dot", spikethickness=1,
    ),
    hoverlabel=dict(
        bgcolor="rgba(15,23,42,0.95)",
        bordercolor="rgba(6,182,212,0.5)",
        font=dict(size=13, color="#f1f5f9", family="Inter"),
    ),
)


def _apply_theme(fig):
    """Apply the dark theme config to a figure."""
    fig.update_layout(**_DARK_LAYOUT)
    return fig
