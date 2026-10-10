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
        "labelAngle": 0,
        "labelColor": c.color_secondary,
        "labelFontSize": c.size_small,
        "labelFontWeight": c.font_weight,
        "tickColor": c.color_secondary,
        "tickSize": 5,
        "titleColor": c.color_primary,
        "titleFontSize": c.size_medium,
        "titleFontWeight": c.font_weight,
    }
    axis_x: AxisConfigKwds = {
        "titleAnchor": "end",
        "titleAlign": "center",
    }
    axis_y: AxisConfigKwds = {
        "titleAlign": "center",
        "titleAnchor": "end",
        "titleAngle": 0,
        "titleX": 0,
        "titleY": -15,
    }
    legend: LegendConfigKwds = {
        "labelColor": c.color_primary,
        "labelFontSize": c.size_small,
        "labelFontWeight": c.font_weight,
        "labelLimit": 0,
        "titleColor": c.color_primary,
        "titleFontSize": c.size_medium,
        "titleFontWeight": c.font_weight,
    }
    config_kwds: ConfigKwds = {
        "axis": axis,
        "axisX": axis_x,
        "axisY": axis_y,
        "concat": {"spacing": c.spacing_concat},
        "facet": {"spacing": c.spacing_facet},
        "header": header,
        "legend": legend,
        "text": {"color": c.color_primary, "fontSize": c.size_small},
        "title": title,
        "view": view,
    }
    return {"config": config_kwds}


@alt.theme.register("camminady", enable=True)
def camminady() -> ThemeConfig:
    return build_theme(config)
