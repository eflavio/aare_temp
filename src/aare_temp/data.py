"""Load plot data from hydrodaten.admin.ch."""

import requests


def load_plot_data(station_id: str, plot_type: str = "temperature"):
    """
    Fetch JSON plot data for a hydrological station.

    Args:
        station_id: Hydrological station identifier.
        plot_type: 'temperature' or 'flow' (Abfluss & Wasserstand).

    Returns:
        dict: Raw plot data as returned by the API.
    """
    if plot_type == "temperature":
        url = (
            f"https://www.hydrodaten.admin.ch/plots/temperature_7days/"
            f"{station_id}_temperature_7days_de.json"
        )
    else:
        url = (
            f"https://www.hydrodaten.admin.ch/plots/p_q_7days/"
            f"{station_id}_p_q_7days_de.json"
        )

    response = requests.get(url, timeout=15)
    response.raise_for_status()
    raw = response.json()
    # API nests series data under "plot.data"
    return raw.get("plot", raw)
