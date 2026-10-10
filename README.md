# camminady_altair_theme

A minimal [Altair](https://altair-viz.github.io) theme: muted gray text,
dashed grid lines, no frame around the plot, and horizontal axis titles at the
end of each axis. It comes in a light (`camminady`) and a dark
(`camminady_dark`) variant.

![Single Chart](https://raw.githubusercontent.com/thomascamminady/camminady_altair_theme/main/assets/single_chart.png)

## Installation

```bash
uv add camminady-altair-theme
# or
pip install camminady-altair-theme
```

Requires Python 3.11+ and Altair 6.

## Usage

```python
import altair as alt

alt.theme.enable("camminady")  # or "camminady_dark"
```

There is no need to import the package: it registers both themes through
Altair's theme entry points. Importing `camminady_altair_theme` registers the
themes but does not enable them (before 0.2.0, importing the package enabled
the theme).

To use the theme for a single chart only:

```python
with alt.theme.enable("camminady"):
    chart.save("chart.png")
```

### Customising

All colours, font sizes and default dimensions are fields of `Config`. Build
your own variant from it:

```python
import altair as alt
from camminady_altair_theme import Config, build_theme


@alt.theme.register("camminady_small", enable=True)
def camminady_small() -> alt.theme.ThemeConfig:
    return build_theme(Config(width=400, height=250))
```

Individual charts can still override anything with `chart.configure_*(...)`.

### Colour-blind safety

The theme keeps Vega's default `tableau10` category palette. Its third (red)
and fifth (green) colours are nearly indistinguishable for people with
deuteranopia, so for five or more categories use the bundled Okabe-Ito
palette:

```python
from camminady_altair_theme import OKABE_ITO

chart.encode(color=alt.Color("group:N").scale(range=OKABE_ITO))
```

### Layout notes

- Single views are 800 × 400 px by default, for continuous and discrete axes.
- The y-axis title sits horizontally above the y axis and the x-axis title at
  the right end of the x axis. Legends (also with `orient="top"`) and facet
  headers are placed so that they do not overlap these titles.
- X-axis labels are horizontal, also for categorical axes. For many or long
  category names, rotate them (`alt.Axis(labelAngle=-45)`) or use a
  horizontal bar chart.
- With an x axis at the top (`orient="top"`), the y-axis title overlaps its
  labels; move it up with `alt.Y(..., axis=alt.Axis(titleY=-45))`.

## Examples

A simple chart.

![Single Chart](https://raw.githubusercontent.com/thomascamminady/camminady_altair_theme/main/assets/single_chart.png)

And a faceted version.

![Facet Chart](https://raw.githubusercontent.com/thomascamminady/camminady_altair_theme/main/assets/facet_chart.png)

## Development

```bash
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run ty check
uv run python create_charts.py  # regenerate the images above
```
