"""Fäbu's App – Aare & Reuss Wasser-Monitoring"""

import dash

# Create the Dash app first so callbacks can register on it
app = dash.Dash(__name__, title="Fäbu's App – Aare & Reuss Monitor")
server = app.server

# Now import components and callbacks (they register on `app` above)
from components import wave_svg, APP_INDEX_TEMPLATE, build_layout
from callbacks import update_plots  # noqa: F401 – registers the callback

# Inject custom HTML (CSS is loaded automatically from assets/style.css)
template = APP_INDEX_TEMPLATE.replace("__DASH_WAVE_SVG__", wave_svg())
template = template.replace("__DASH_METAS__", "{%metas%}")
template = template.replace("__DASH_TITLE__", "{%title%}")
template = template.replace("__DASH_FAVICON__", "{%favicon%}")
app.index_string = template

app.layout = build_layout()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
