"""Dash callbacks for data fetching and plot updates."""

import datetime

from dash import callback, Output, Input

from data import load_plot
from plots import build_combined_plot, apply_dark_theme


def fmt_time(raw_time):
    """Format ISO-ish time to readable Swiss format."""
    if not raw_time:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
        return dt.strftime("%d.%m. %H:%M")
    except (ValueError, TypeError):
        return raw_time


@callback(
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
