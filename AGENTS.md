# Fäbu's App – Aare & Reuss Water Monitoring

A live dashboard that visualises temperature, flow rate, and water level data for the Swiss rivers Aare and Reuss, fetched from [hydrodaten.admin.ch](https://www.hydrodaten.admin.ch).

## Structure

```
pyproject.toml      ← Package config. Python ≥3.11, dependencies: dash, gunicorn, requests.
src/aare_temp/__init__.py  ← Package root (empty, enables `import aare_temp`).
src/aare_temp/main.py      ← Entry point. Creates the Dash app, imports layout and callbacks.
src/aare_temp/components.py ← Reusable UI builders (measurement cards, graph containers, section headers).
src/aare_temp/callbacks.py  ← Dash callbacks. Fetches data, builds plots, updates all outputs.
src/aare_temp/data.py       ← API client. Fetches JSON from hydrodaten.admin.ch.
src/aare_temp/plots.py      ← Plotly helpers. Build figures using go.Figure/go.Scatter.
src/aare_temp/assets/style.css ← Global dark theme (glass-morphism cards, gradients, responsive).
```

The project follows a **src layout** (`src/` directory) so that the package is always imported from the installed location, not the source tree. This avoids import shadows during development and testing.

## How it works

1. **Data** (`src/aare_temp/data.py`): `load_plot_data(station_id, plot_type)` fetches JSON from the Swiss hydrology API. Two station IDs: `2135` (Aare, Thun) and `2152` (Reuss, Aarau).
2. **Plots** (`src/aare_temp/plots.py`): `build_single_plot(data, label)` and `build_combined_plot(data_aare, data_reuss)` create Plotly figures with a shared dark theme.
3. **UI** (`src/aare_temp/components.py`): `build_layout()` assembles the page from composable builders: `measurement_card()`, `graph_card()`, `section_header()`.
4. **Callback** (`src/aare_temp/callbacks.py`): `update_plots` fires every 10 minutes, fetches all data, builds 6 figures, extracts latest values, and updates 19 outputs.
5. **App** (`src/aare_temp/main.py`): Wires it all together. Uses `external_stylesheets` for Google Fonts. Exposes `app.server` for gunicorn.

The CLI entry point `aare-temp` (defined in `pyproject.toml`) runs `aare_temp:main.main`, which calls `app.run()`.

## Key conventions

- River colors are centralised in `src/aare_temp/plots.py` (`RIVER_COLORS`).
- The dark theme is a single constant `_DARK_LAYOUT` in `src/aare_temp/plots.py`.
- All graph and value IDs are defined in `src/aare_temp/components.py` and referenced by callbacks.
- The layout is fully responsive via CSS media queries — no inline style overrides needed.
- Dash automatically picks up `src/aare_temp/assets/style.css` — keep it there; don't move it to the project root.
