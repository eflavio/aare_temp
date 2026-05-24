"""Fäbu's App – Aare & Reuss Wasser-Monitoring."""

from dash import Dash

from aare_temp.components import build_layout
from aare_temp.callbacks import update_plots  # noqa: F401 – registers the callback

app = Dash(
    __name__,
    title="Fäbu's App – Aare & Reuss Monitor",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
    ],
)

app.layout = build_layout()
server = app.server


def main():
    app.run(host="0.0.0.0")
