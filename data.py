"""Data loading from hydrodaten.admin.ch."""

import requests


def load_plot(station_id: str = "2135", title: str = "Aare", plot_type: str = "temperature"):
    """
    Load plot data from hydrodaten.admin.ch.

    Args:
        station_id: Hydrological station identifier.
        title: Display title for the plot.
        plot_type: Either 'temperature' or 'flow' (for Abfluss und Wasserstand).

    Returns:
        tuple: (plot_data, latest_values)
               where latest_values is a dict with keys 'value', 'unit', 'time'
                       (for flow type, it may contain 'flow' and 'level' sub-dicts).
    """
    if plot_type == "temperature":
        url = (
            f"https://www.hydrodaten.admin.ch/plots/temperature_7days/"
            f"{station_id}_temperature_7days_de.json"
        )
    else:  # flow and water level
        url = (
            f"https://www.hydrodaten.admin.ch/plots/p_q_7days/"
            f"{station_id}_p_q_7days_de.json"
        )

    response = requests.get(url)
    data = response.json()

    # Add hover info for all data series in the plot
    for series in data["plot"]["data"]:
        if "hoverinfo" in series:
            series["hoverinfo"] = "x+y+name"

    # Extract latest measurements
    latest_values = {}
    if plot_type == "temperature":
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
