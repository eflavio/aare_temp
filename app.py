import dash
from dash import dcc, html, Output, Input
import requests


# Load your JSON once here or dynamically inside the callback
def load_plot(station_id="2135", title="Aare", plot_type="temperature"):
    """
    Load plot data from hydrodaten.admin.ch
    plot_type can be 'temperature' or 'flow' (for Abfluss und Wasserstand)
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

    # Update the layout title with proper Dash format
    data["plot"]["layout"]["title"] = {"text": title, "font": {"size": 24}}
    return data["plot"]


app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.H1(
            "Fäbu's App",
            style={"textAlign": "center", "marginBottom": "20px"},
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
    ],
    style={"fontFamily": "Arial, sans-serif", "padding": "20px"},
)


@app.callback(
    [
        Output("aare-temp-graph", "figure"),
        Output("aare-flow-graph", "figure"),
        Output("reuss-temp-graph", "figure"),
        Output("reuss-flow-graph", "figure"),
    ],
    Input("interval-refresh", "n_intervals"),
)
def update_plots(n):
    # Get temperature plots
    aare_temp_plot = load_plot(
        station_id="2135", title="Temperatur", plot_type="temperature"
    )
    reuss_temp_plot = load_plot(
        station_id="2152", title="Temperatur", plot_type="temperature"
    )

    # Get flow and water level plots
    aare_flow_plot = load_plot(
        station_id="2135", title="Abfluss und Wasserstand", plot_type="flow"
    )
    reuss_flow_plot = load_plot(
        station_id="2152", title="Abfluss und Wasserstand", plot_type="flow"
    )

    # Additional layout adjustments to ensure titles are visible
    for plot in [aare_temp_plot, reuss_temp_plot, aare_flow_plot, reuss_flow_plot]:
        plot["layout"]["margin"] = {"t": 50}  # Add top margin for title
        plot["layout"]["title"]["x"] = 0.5  # Center the title

    return aare_temp_plot, aare_flow_plot, reuss_temp_plot, reuss_flow_plot


if __name__ == "__main__":
    app.run(debug=True)
