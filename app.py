import dash
from dash import dcc, html, Output, Input
import requests


# Load your JSON once here or dynamically inside the callback
def load_plot():
    url = "https://www.hydrodaten.admin.ch/plots/temperature_7days/2135_temperature_7days_de.json"
    response = requests.get(url)
    data = response.json()
    data["plot"]["data"][0]["hoverinfo"] = "x+y+name"
    return data["plot"]


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="my-graph"),
        dcc.Interval(
            id="interval-refresh", interval=10 * 60 * 1000, n_intervals=0
        ),  # 10 min
    ]
)


@app.callback(Output("my-graph", "figure"), Input("interval-refresh", "n_intervals"))
def update_plot(n):
    return load_plot()


def run():
    app.run(debug=True)


if __name__ == "__main__":
    run()
