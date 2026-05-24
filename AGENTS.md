# Fäbu's App – Aare & Reuss Water Monitoring

A live dashboard that visualises temperature, flow rate, and water level data for the Swiss rivers Aare and Reuss, fetched from [hydrodaten.admin.ch](https://www.hydrodaten.admin.ch).

## Structure

```
app.py              ← Entry point. Creates the Dash app, imports layout and callbacks.
components.py       ← Reusable UI builders (measurement cards, graph containers, section headers).
callbacks.py        ← Dash callbacks. Fetches data, builds plots, updates all outputs.
data.py             ← API client. Fetches JSON from hydrodaten.admin.ch.
plots.py            ← Plotly helpers. Build figures using go.Figure/go.Scatter.
assets/style.css    ← Global dark theme (glass-morphism cards, gradients, responsive).
pyproject.toml      ← Python ≥3.11, dependencies: dash, gunicorn, requests.
```

## How it works

1. **Data** (`data.py`): `load_plot_data(station_id, plot_type)` fetches JSON from the Swiss hydrology API. Two station IDs: `2135` (Aare, Thun) and `2152` (Reuss, Aarau).
2. **Plots** (`plots.py`): `build_single_plot(data, label)` and `build_combined_plot(data_aare, data_reuss)` create Plotly figures with a shared dark theme.
3. **UI** (`components.py`): `build_layout()` assembles the page from composable builders: `measurement_card()`, `graph_card()`, `section_header()`.
4. **Callback** (`callbacks.py`): `update_plots` fires every 10 minutes, fetches all data, builds 6 figures, extracts latest values, and updates 19 outputs.
5. **App** (`app.py`): Wires it all together. Uses `external_stylesheets` for Google Fonts.

## Key conventions

- River colors are centralised in `plots.py` (`RIVER_COLORS`).
- The dark theme is a single constant `_DARK_LAYOUT` in `plots.py`.
- All graph and value IDs are defined in `components.py` and referenced by callbacks.
- The layout is fully responsive via CSS media queries — no inline style overrides needed.
