"""Fäbu's App – Aare & Reuss Wasser-Monitoring."""

from dash import Dash

from components import build_layout
from callbacks import update_plots  # noqa: F401 – registers the callback

app = Dash(
    __name__,
    title="Fäbu's App – Aare & Reuss Monitor",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
    ],
)

app.layout = build_layout()
server = app.server


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
