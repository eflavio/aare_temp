"""Dash callbacks for data fetching and plot updates."""

import datetime

from dash import callback, Output, Input

from aare_temp.data import load_plot_data
from aare_temp.plots import build_single_plot, build_combined_plot, build_filtered_single_plot, build_filtered_combined_plot


# ── Helpers ────────────────────────────────────────────────────────────────

def _fmt_time(raw):
    """Format ISO-ish time to Swiss format."""
    if not raw:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.strftime("%d.%m. %H:%M")
    except (ValueError, TypeError):
        return raw


def _latest_values(raw_data, plot_type):
    """Extract latest measurement(s) from raw API data."""
    if not raw_data.get("data"):
        return None

    if plot_type == "temperature":
        series = raw_data["data"][0]
        return {
            "value": series["y"][-1],
            "unit": "°C",
            "time": series["x"][-1],
        }

    values = {}
    for series in raw_data["data"]:
        if not (series.get("x") and series.get("y")):
            continue
        name = series.get("name", "")
        latest = {"value": series["y"][-1], "time": series["x"][-1]}
        if "Abfluss" in name:
            values["flow"] = {**latest, "unit": "m³/s"}
        elif "Wasserstand" in name or "Pegel" in name:
            values["level"] = {**latest, "unit": "m"}

    return values if values else None


# ── Callback ───────────────────────────────────────────────────────────────

@callback(
    [
        # Graphs
        Output("combined-temp-graph", "figure"),
        Output("combined-flow-graph", "figure"),
        Output("combined-level-graph", "figure"),
        Output("aare-temp-graph", "figure"),
        Output("aare-flow-graph", "figure"),
        Output("aare-level-graph", "figure"),
        Output("reuss-temp-graph", "figure"),
        Output("reuss-flow-graph", "figure"),
        Output("reuss-level-graph", "figure"),
        # Latest values
        Output("aare-temp-value", "children"),
        Output("aare-flow-value", "children"),
        Output("aare-level-value", "children"),
        Output("reuss-temp-value", "children"),
        Output("reuss-flow-value", "children"),
        Output("reuss-level-value", "children"),
        # Timestamps
        Output("aare-temp-time", "children"),
        Output("aare-flow-time", "children"),
        Output("aare-level-time", "children"),
        Output("reuss-temp-time", "children"),
        Output("reuss-flow-time", "children"),
        Output("reuss-level-time", "children"),
        # Last updated
        Output("last-updated", "children"),
    ],
    Input("interval-refresh", "n_intervals"),
)
def update_plots(_):
    # ── Fetch & build plots ─────────────────────────────────────
    aare_temp_raw = load_plot_data("2135", "temperature")
    aare_flow_raw = load_plot_data("2135", "flow")
    reuss_temp_raw = load_plot_data("2152", "temperature")
    reuss_flow_raw = load_plot_data("2152", "flow")

    # Individual plots
    aare_temp_fig = build_single_plot(aare_temp_raw, "Aare", "°C")
    reuss_temp_fig = build_single_plot(reuss_temp_raw, "Reuss", "°C")
    aare_flow_fig = build_filtered_single_plot(aare_flow_raw, "Aare", "Abfluss", "m³/s")
    reuss_flow_fig = build_filtered_single_plot(reuss_flow_raw, "Reuss", "Abfluss", "m³/s")
    aare_level_fig = build_filtered_single_plot(aare_flow_raw, "Aare", "Wasserstand", "m")
    reuss_level_fig = build_filtered_single_plot(reuss_flow_raw, "Reuss", "Wasserstand", "m")

    # Combined comparison
    combined_temp = build_combined_plot(aare_temp_raw, reuss_temp_raw, "°C")
    combined_flow = build_filtered_combined_plot(aare_flow_raw, reuss_flow_raw, "Abfluss", "m³/s")
    combined_level = build_filtered_combined_plot(aare_flow_raw, reuss_flow_raw, "Wasserstand", "m")

    # ── Extract latest values ───────────────────────────────────
    aare_temp_val = _latest_values(aare_temp_raw, "temperature")
    aare_flow_val = _latest_values(aare_flow_raw, "flow")
    reuss_temp_val = _latest_values(reuss_temp_raw, "temperature")
    reuss_flow_val = _latest_values(reuss_flow_raw, "flow")

    # ── Format display strings ──────────────────────────────────
    def _val_str(v):
        if v is None:
            return "N/A"
        if "unit" in v:
            fmt = ".2f" if v["unit"] == "m" else ".1f"
            return f'{v["value"]:{fmt}} {v["unit"]}'
        return str(v)

    def _time_str(v):
        return _fmt_time(v["time"]) if v else "–"

    # ── Find the most recent data timestamp ─────────────────────
    all_times = [v["time"] for v in [aare_temp_val, reuss_temp_val] if v] + \
                [v["flow"]["time"] for v in [aare_flow_val, reuss_flow_val] if v and "flow" in v] + \
                [v["level"]["time"] for v in [aare_flow_val, reuss_flow_val] if v and "level" in v]
    latest_time = max(all_times) if all_times else None
    last_updated = f"Letzte Aktualisierung: {_fmt_time(latest_time)}" if latest_time else ""

    # ── Return everything ───────────────────────────────────────
    return (
        # Graphs
        combined_temp, combined_flow, combined_level,
        aare_temp_fig, aare_flow_fig, aare_level_fig, reuss_temp_fig, reuss_flow_fig, reuss_level_fig,
        # Values
        _val_str(aare_temp_val),
        _val_str(aare_flow_val.get("flow") if aare_flow_val else None),
        _val_str(aare_flow_val.get("level") if aare_flow_val else None),
        _val_str(reuss_temp_val),
        _val_str(reuss_flow_val.get("flow") if reuss_flow_val else None),
        _val_str(reuss_flow_val.get("level") if reuss_flow_val else None),
        # Timestamps
        _time_str(aare_temp_val),
        _time_str(aare_flow_val.get("flow") if aare_flow_val else None),
        _time_str(aare_flow_val.get("level") if aare_flow_val else None),
        _time_str(reuss_temp_val),
        _time_str(reuss_flow_val.get("flow") if reuss_flow_val else None),
        _time_str(reuss_flow_val.get("level") if reuss_flow_val else None),
        # Last updated
        last_updated,
    )
