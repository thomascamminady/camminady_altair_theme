"""Minimal Altair themes with muted gray text and dashed grid lines.

Importing this module registers two themes with Altair without enabling
them: ``"camminady"`` (light) and ``"camminady_dark"``. Both are also
declared as ``altair.vegalite.v6.theme`` entry points, so enabling them
does not require an import::

    import altair as alt

    alt.theme.enable("camminady")
"""

from dataclasses import dataclass
from typing import Final, Literal, LiteralString

import altair as alt
from altair.theme import (
    AxisConfigKwds,
    ConfigKwds,
    HeaderConfigKwds,
    LegendConfigKwds,
    ThemeConfig,
    TitleConfigKwds,
    ViewConfigKwds,
)

FontWeight = Literal[
    "normal",
    "bold",
    "lighter",
    "bolder",
    100,
    200,
    300,
    400,
    500,
    600,
    700,
    800,
    900,
]

OKABE_ITO: Final[tuple[LiteralString, ...]] = (
    "#0072b2",  # blue
    "#e69f00",  # orange
    "#009e73",  # bluish green
    "#cc79a7",  # reddish purple
    "#56b4e9",  # sky blue
    "#d55e00",  # vermillion
    "#f0e442",  # yellow
)
"""Okabe-Ito palette (without black), ordered blue and orange first.

The themes keep Vega's default ``tableau10`` category palette, in which the
3rd (red) and 5th (green) colour are nearly indistinguishable with
deuteranopia. Use this palette when a chart has more than four categories,
e.g. ``alt.Color("x:N").scale(range=OKABE_ITO)``.
"""


@dataclass
class Config:
    """Design tokens from which the theme is built.

    Attributes
    ----------
    color_primary
        Titles, legends and text marks.
    color_secondary
        Axis labels, ticks, domain lines, facet labels and subtitles.
    color_background
        Background of the whole chart.
    color_grid
        Dashed grid lines.
    color_rule
        Rule marks, including error bars and boxplot whiskers.
    font_weight
        Weight of all text.
    size_small
        Font size of labels and text marks.
    size_medium
        Font size of axis, legend and facet titles and of subtitles.
    size_large
        Font size of chart titles.
    height
        Default height of a single view in pixels.
    width
        Default width of a single view in pixels.
    spacing_facet
        Spacing between facets in pixels.
    spacing_concat
        Spacing between concatenated charts in pixels.
    y_title_offset
        Distance between the top of the plot area and the baseline of the
        horizontal y-axis title in pixels.
    """

    color_primary: LiteralString = "dimgray"
    # "gray" (#808080) has a contrast of 3.9:1 on white, below the 4.5:1 that
    # WCAG AA requires for small text such as tick labels; #767676 passes.
    color_secondary: LiteralString = "#767676"
    color_background: LiteralString = "white"
    color_grid: LiteralString = "#dddddd"
    color_rule: LiteralString = "black"
    font_weight: FontWeight = "normal"
    size_small: int = 12
    size_medium: int = 14
    size_large: int = 20
    height: int = 400
    width: int = 800
    spacing_facet: int = 40
    spacing_concat: int = 40
    y_title_offset: int = 15


config = Config()
"""Tokens of the ``"camminady"`` theme, read each time a chart is rendered."""

config_dark = Config(
    color_primary="#a9a9a9",
    color_secondary="#8c8c8c",
    color_background="#1e1e1e",
    color_grid="#3a3a3a",
    color_rule="lightgray",
)
"""Tokens of the ``"camminady_dark"`` theme."""


def build_theme(c: Config) -> ThemeConfig:
    """Build the Vega-Lite theme for the given design tokens.

    Parameters
    ----------
    c
        Colors, font sizes and dimensions of the theme.

    Returns
    -------
    ThemeConfig
        A fresh dictionary that can be returned by an Altair theme function.
    """
    # The size applies to continuous and discrete axes alike, which matches
    # the deprecated `view.width`/`view.height` keys used previously.
    view: ViewConfigKwds = {
        "continuousWidth": c.width,
        "continuousHeight": c.height,
        "discreteWidth": c.width,
        "discreteHeight": c.height,
        "strokeWidth": 0,
    }
    # Facet headers are styled via `header` (not `headerRow` etc.) so that
    # `chart.configure_header(...)` still takes effect for users.
    header: HeaderConfigKwds = {
        "titleColor": c.color_primary,
        "titleFontSize": c.size_medium,
        "titleFontWeight": c.font_weight,
        "labelColor": c.color_secondary,
        "labelFontSize": c.size_small,
        "labelFontWeight": c.font_weight,
    }
    # Column headers are placed relative to the plot area and would overlap
    # the horizontal y-axis title above it; lift them above that title.
    header_top: HeaderConfigKwds = {
        "labelPadding": c.y_title_offset + c.size_medium,
    }
    title: TitleConfigKwds = {
        "anchor": "middle",
        "color": c.color_primary,
        "fontSize": c.size_large,
        "fontWeight": c.font_weight,
        "subtitleColor": c.color_secondary,
        "subtitleFontSize": c.size_medium,
        "subtitleFontWeight": c.font_weight,
    }
    axis: AxisConfigKwds = {
        "domain": True,
        "domainColor": c.color_secondary,
        "domainWidth": 1,
        "gridCap": "round",
        "gridColor": c.color_grid,
        "gridDash": [2, 4],
        "gridWidth": 1,
        "labelColor": c.color_secondary,
        "labelFontSize": c.size_small,
        "labelFontWeight": c.font_weight,
        "tickColor": c.color_secondary,
        "tickSize": 5,
        "titleColor": c.color_primary,
        "titleFontSize": c.size_medium,
        "titleFontWeight": c.font_weight,
    }
    # Axis titles sit at the "end" of their axis: the x title below the
    # right end of the x axis, the y title horizontally above the y axis.
    # They are aligned so that they never extend beyond the plot area, where
    # they would collide with legends or grow the chart outwards.
    axis_x: AxisConfigKwds = {
        # Horizontal labels also for discrete x axes (Vega-Lite rotates them
        # by default). Only set for x: on y axes a labelAngle makes
        # Vega-Lite right-align the labels of right-oriented axes, which
        # draws them over the ticks and into the plot.
        "labelAngle": 0,
        "titleAnchor": "end",
        "titleAlign": "right",
    }
    axis_y: AxisConfigKwds = {
        "titleAlign": "left",
        "titleAnchor": "end",
        "titleAngle": 0,
        "titleBaseline": "bottom",
        "titleX": 0,
        "titleY": -c.y_title_offset,
    }
    axis_right: AxisConfigKwds = {
        "titleAlign": "right",
    }
    legend: LegendConfigKwds = {
        "labelColor": c.color_primary,
        "labelFontSize": c.size_small,
        "labelFontWeight": c.font_weight,
        "labelLimit": 0,
        # Legends with orient="top" are placed relative to the plot area and
        # ignore the y-axis title above it; offset them past that title.
        "offset": c.y_title_offset + c.size_medium + 5,
        "titleColor": c.color_primary,
        "titleFontSize": c.size_medium,
        "titleFontWeight": c.font_weight,
    }
    config_kwds: ConfigKwds = {
        "background": c.color_background,
        "axis": axis,
        "axisX": axis_x,
        "axisY": axis_y,
        "axisRight": axis_right,
        "concat": {"spacing": c.spacing_concat},
        "facet": {"spacing": c.spacing_facet},
        "header": header,
        "headerColumn": header_top,
        "headerFacet": header_top,
        "legend": legend,
        "rule": {"color": c.color_rule},
        "text": {"color": c.color_primary, "fontSize": c.size_small},
        "title": title,
        "view": view,
    }
    return {"config": config_kwds}


# Registering does not enable the themes: importing a library should not
# change global state. Use `alt.theme.enable("camminady")`, which also works
# without importing this package thanks to the entry points.
@alt.theme.register("camminady", enable=False)
def camminady() -> ThemeConfig:
    """Light theme: gray text and dashed grid lines on white."""
    return build_theme(config)


@alt.theme.register("camminady_dark", enable=False)
def camminady_dark() -> ThemeConfig:
    """Dark theme: the same layout with light gray text on a dark background."""
    return build_theme(config_dark)
