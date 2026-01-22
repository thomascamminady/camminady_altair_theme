from dataclasses import dataclass

import altair as alt


@dataclass
class Config:
    primary_color: str = "dimgray"
    secondaray_color: str = "gray"
    font_weight: str = "normal"
    small_font_size: int = 12
    medium_font_size: int = 14
    large_font_size: int = 20
    height: int = 400
    width: int = 800
    spacing_facet: int = 40
    spacing_concat: int = 40


config = Config()


# @alt.theme.register("camminady", enable=True)
def camminady() -> alt.theme.ThemeConfig:
    return {
        "config": {
            "text": {
                "color": config.primary_color,
                "fontSize": config.small_font_size,
            },
            "title": {
                "anchor": "middle",
                "fontWeight": config.font_weight,
                "fontSize": config.large_font_size,
                "color": config.primary_color,
            },
            "header": {
                "titleFontSize": config.large_font_size,
                "labelFontSize": config.medium_font_size,
                "titleColor": config.primary_color,
                "labelColor": config.primary_color,
                "titleFontWeight": config.font_weight,
                "labelFontWeight": config.font_weight,
            },
            "view": {
                "height": config.height,
                "width": config.width,
                "strokeWidth": 0,
                "fill": "white",
            },
            "facet": {
                "color": "red",
                "spacing": config.spacing_facet,
            },
            "concat": {
                "spacing": config.spacing_concat,
            },
            "headerRow": (
                subplotheader := {
                    "labelColor": config.secondaray_color,
                    "labelFontSize": config.small_font_size,
                    "titleColor": config.primary_color,
                    "titleFontSize": config.medium_font_size,
                }
            ),
            "headerFacet": subplotheader,
            "headerColumn": subplotheader,
            "axis": {
                "domain": True,
                "domainColor": config.secondaray_color,
                "domainWidth": 1,
                "gridWidth": 1,
                "labelAngle": 0,
                "tickSize": 5,
                "gridCap": "round",
                "gridDash": [2, 4],
                "titleFontWeight": config.font_weight,
                "labelFontWeight": config.font_weight,
                "titleFontSize": config.medium_font_size,
                "labelFontSize": config.small_font_size,
                "titleColor": config.primary_color,
                "labelColor": config.secondaray_color,
                "tickColor": config.secondaray_color,
            },
            "axisX": {
                "titleAnchor": "end",
                "titleAlign": "center",
            },
            "axisY": {
                "titleAnchor": "end",
                "titleAngle": 0,
                "titleAlign": "center",
                "titleY": -15,
                "titleX": 0,
            },
            "legend": {
                "titleFontWeight": config.font_weight,
                "labelFontWeight": config.font_weight,
                "titleFontSize": config.medium_font_size,
                "labelFontSize": config.small_font_size,
                "labelLimit": 0,
                "titleColor": config.primary_color,
                "labelColor": config.primary_color,
            },
        }
    }
