import dash
from dash import dcc, html, Output, Input
import requests
import datetime


# Load your JSON once here or dynamically inside the callback
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

    # Update the layout title with proper Dash format
    data["plot"]["layout"]["title"] = {"text": title, "font": {"size": 24}}
    return data["plot"], latest_values


app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.H1(
            "Fäbu's App",
            style={"textAlign": "center", "marginBottom": "20px"},
        ),
        # Latest measurements dashboard section
        html.Div(
            [
                html.H2(
                    "Aktuelle Messwerte",
                    style={"textAlign": "center", "marginBottom": "15px"},
                ),
                # Display grid for measurements
                html.Div(
                    [
                        # Aare latest measurements
                        html.Div(
                            [
                                html.H3(
                                    "Aare",
                                    style={
                                        "textAlign": "center",
                                        "marginBottom": "10px",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Temperatur:",
                                                    className="measurement-label",
                                                ),
                                                html.Div(
                                                    id="aare-temp-value",
                                                    className="measurement-value",
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Abfluss:",
                                                    className="measurement-label",
                                                ),
                                                html.Div(
                                                    id="aare-flow-value",
                                                    className="measurement-value",
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Wasserstand:",
                                                    className="measurement-label",
                                                ),
                                                html.Div(
                                                    id="aare-level-value",
                                                    className="measurement-value",
                                                ),
                                            ]
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "gap": "10px",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "padding": "15px",
                                "border": "1px solid #ddd",
                                "borderRadius": "5px",
                                "background": "#f9f9f9",
                            },
                        ),
                        # Reuss latest measurements
                        html.Div(
                            [
                                html.H3(
                                    "Reuss",
                                    style={
                                        "textAlign": "center",
                                        "marginBottom": "10px",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Temperatur:",
                                                    className="measurement-label",
                                                ),
                                                html.Div(
                                                    id="reuss-temp-value",
                                                    className="measurement-value",
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Abfluss:",
                                                    className="measurement-label",
                                                ),
                                                html.Div(
                                                    id="reuss-flow-value",
                                                    className="measurement-value",
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Wasserstand:",
                                                    className="measurement-label",
                                                ),
                                                html.Div(
                                                    id="reuss-level-value",
                                                    className="measurement-value",
                                                ),
                                            ]
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "gap": "10px",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "padding": "15px",
                                "border": "1px solid #ddd",
                                "borderRadius": "5px",
                                "background": "#f9f9f9",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "gap": "20px",
                        "marginBottom": "10px",
                        "flexWrap": "wrap",
                    },
                ),
                # Last updated time
                html.Div(
                    id="last-updated",
                    style={
                        "textAlign": "right",
                        "fontSize": "12px",
                        "fontStyle": "italic",
                        "marginTop": "5px",
                    },
                ),
            ],
            style={
                "width": "100%",
                "padding": "15px",
                "marginBottom": "20px",
                "border": "1px solid #ddd",
                "borderRadius": "5px",
                "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
            },
        ),
        # Aare section
        html.Div(
            [
                html.H2("Aare", style={"textAlign": "center"}),
                dcc.Graph(
                    id="aare-temp-graph",
                    config={"displayModeBar": False},
                    style={"height": "40vh"},
                ),
                dcc.Graph(
                    id="aare-flow-graph",
                    config={"displayModeBar": False},
                    style={"height": "40vh"},
                ),
            ],
            style={
                "width": "100%",
                "padding": "10px",
                "marginBottom": "20px",
                "border": "1px solid #ddd",
                "borderRadius": "5px",
            },
        ),
        # Reuss section
        html.Div(
            [
                html.H2("Reuss", style={"textAlign": "center"}),
                dcc.Graph(
                    id="reuss-temp-graph",
                    config={"displayModeBar": False},
                    style={"height": "40vh"},
                ),
                dcc.Graph(
                    id="reuss-flow-graph",
                    config={"displayModeBar": False},
                    style={"height": "40vh"},
                ),
            ],
            style={
                "width": "100%",
                "padding": "10px",
                "border": "1px solid #ddd",
                "borderRadius": "5px",
            },
        ),
        dcc.Interval(
            id="interval-refresh", interval=10 * 60 * 1000, n_intervals=0
        ),  # 10 min
        # CSS styles
        # html.Style("""
        #     .measurement-label {
        #         font-weight: bold;
        #         margin-right: 10px;
        #         display: inline-block;
        #         width: 120px;
        #     }
        #     .measurement-value {
        #         font-size: 18px;
        #         font-weight: bold;
        #         display: inline-block;
        #     }
        #     @media (max-width: 768px) {
        #         #measurement-grid {
        #             flex-direction: column;
        #         }
        #     }
        # """),
    ],
    style={"fontFamily": "Arial, sans-serif", "padding": "20px"},
)


@app.callback(
    [
        # Graph figures
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
        station_id="2135", title="Abfluss und Wasserstand", plot_type="flow"
    )
    reuss_flow_plot, reuss_flow_latest = load_plot(
        station_id="2152", title="Abfluss und Wasserstand", plot_type="flow"
    )

    # Additional layout adjustments to ensure titles are visible
    for plot in [aare_temp_plot, reuss_temp_plot, aare_flow_plot, reuss_flow_plot]:
        plot["layout"]["margin"] = {"t": 50}  # Add top margin for title
        plot["layout"]["title"]["x"] = 0.5  # Center the title

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

    return (
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
        last_updated,
    )


if __name__ == "__main__":
    app.run(debug=True)
