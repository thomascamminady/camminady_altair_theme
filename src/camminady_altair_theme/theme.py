from dataclasses import dataclass
from typing import Literal, LiteralString

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


@dataclass
class Config:
    color_primary: LiteralString = "dimgray"
    color_secondary: LiteralString = "gray"
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
        "fill": "white",
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
    }
    axis: AxisConfigKwds = {
        "domain": True,
        "domainColor": c.color_secondary,
        "domainWidth": 1,
        "gridCap": "round",
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
        "text": {"color": c.color_primary, "fontSize": c.size_small},
        "title": title,
        "view": view,
    }
    return {"config": config_kwds}


@alt.theme.register("camminady", enable=True)
def camminady() -> ThemeConfig:
    return build_theme(config)
