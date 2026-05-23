"""Plot building and theming helpers."""


COLOR_MAP = {
    "Aare": "#3b82f6",
    "Reuss": "#06b6d4",
}


def build_combined_plot(aare_data, reuss_data, aare_label, reuss_label, title_text):
    """Merge two river datasets into a single combined Plotly figure."""
    combined = {"data": [], "layout": {"title": {"text": title_text}}}

    # Merge xaxis/yaxis configs from both sources so spike lines etc. work.
    # Use aare as primary, fill missing keys from reuss.
    aare_layout = aare_data.get("layout", {})
    reuss_layout = reuss_data.get("layout", {})

    aare_x = aare_layout.get("xaxis", {})
    reuss_x = reuss_layout.get("xaxis", {})
    combined["layout"]["xaxis"] = {**reuss_x, **aare_x}

    aare_y = aare_layout.get("yaxis", {})
    reuss_y = reuss_layout.get("yaxis", {})
    combined["layout"]["yaxis"] = {**reuss_y, **aare_y}

    for label, data in [(aare_label, aare_data), (reuss_label, reuss_data)]:
        for series in data.get("data", []):
            if "x" not in series or "y" not in series:
                continue
            new_series = {
                "x": series["x"],
                "y": series["y"],
                "name": f"{label} – {series.get('name', '')}",
                "line": {"color": COLOR_MAP.get(label, "#94a3b8"), "width": 2.5},
                "marker": {"size": 5},
                "hoverinfo": "x+y+name",
            }
            combined["data"].append(new_series)

    return combined


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
    for series in plot.get("data", []):
        if "line" in series:
            series["line"].update(width=2.5)
        if "marker" in series:
            series["marker"].update(size=5)

    return plot
