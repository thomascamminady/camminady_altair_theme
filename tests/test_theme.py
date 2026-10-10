"""Tests for the camminady Altair themes.

Altair merges the active theme into a chart's spec *after* validating the
chart, so invalid theme config is silently passed on to Vega-Lite. These
tests therefore validate the theme config against the Vega-Lite JSON schema
explicitly, render charts with vl-convert and check the layout of the
rendered scenegraph.
"""

import functools
import json
import re
import subprocess
import sys
from collections.abc import Iterable
from importlib.metadata import entry_points
from typing import Any, Final, Literal, LiteralString

import altair as alt
import jsonschema
import pytest
import vl_convert as vlc
from altair.vegalite.v6.schema.core import load_schema

from camminady_altair_theme import (
    OKABE_ITO,
    Config,
    build_theme,
    camminady,
    camminady_dark,
)
from camminady_altair_theme import theme as theme_module

Json = Any
"""Parsed JSON (Vega-Lite specs and Vega scenegraphs)."""
Mark = Literal[
    "area",
    "bar",
    "boxplot",
    "errorbar",
    "line",
    "point",
    "rect",
    "rule",
    "text",
]

THEME_NAMES: Final = ("camminady", "camminady_dark")
CONFIGS: Final = {
    "light": theme_module.config,
    "dark": theme_module.config_dark,
    "large": Config(size_small=16, size_medium=22, y_title_offset=24),
}
VL_VERSION: Final = "v" + "_".join(alt.SCHEMA_VERSION[1:].split(".")[:2])
X_TITLE: Final = "Elapsed time since the start of the training block"
Y_TITLE: Final = "Average power per kilogram over the session (W/kg)"
CSS_COLORS: Final = {
    "black": "#000000",
    "dimgray": "#696969",
    "lightgray": "#d3d3d3",
    "white": "#ffffff",
}
RECORDS: Final = [
    {
        "x": i,
        "y": (i * 37) % 11,
        "series": f"series {i % 3}",
        "panel": f"panel {i % 4}",
    }
    for i in range(40)
]


def as_json(obj: object) -> Json:
    """Return a deep copy of ``obj`` made of plain JSON types."""
    return json.loads(json.dumps(obj))


def base(mark: Mark) -> alt.Chart:
    # Pass the mark to the constructor rather than calling `.mark_*()`:
    # with altair >= 6.3, ty cannot infer the return type of those methods.
    return alt.Chart(alt.Data(values=RECORDS), mark=mark)


def line() -> alt.Chart:
    return base("line").encode(x="x:Q", y="y:Q", color="series:N")


GALLERY: Final[dict[str, alt.TopLevelMixin]] = {
    "bar": base("bar").encode(x="series:N", y="sum(y):Q"),
    "line_title_subtitle": line().properties(
        title=alt.Title("Title", subtitle="Subtitle")
    ),
    "scatter_legend": base("point").encode(
        x="x:Q", y="y:Q", color="series:N", shape="series:N"
    ),
    "layer_rule_text": line()
    + base("rule").encode(y="mean(y):Q")
    + base("text").encode(y="mean(y):Q", text=alt.value("mean")),
    "row_facet": line().encode(row="series:N").properties(height=100),
    "wrapped_facet": base("point")
    .encode(x="x:Q", y="y:Q")
    .properties(width=200, height=150)
    .facet(facet="panel:N", columns=2),
    "concat": alt.vconcat(
        line() | base("bar").encode(x=alt.X("y:Q").bin(), y="count():Q"),
        line(),
    ),
    "heatmap": base("rect").encode(x="x:O", y="series:O", color="y:Q"),
    "boxplot": base("boxplot").encode(x="series:N", y="y:Q"),
    "errorbar": base("errorbar").encode(x="series:N", y="y:Q"),
    "stacked_area": base("area").encode(x="x:Q", y="y:Q", color="series:N"),
    "dual_axis": alt.layer(
        base("line").encode(x="x:Q", y="y:Q"),
        base("line").encode(x="x:Q", y="x:Q"),
    ).resolve_scale(y="independent"),
}


def spec_for(chart: alt.TopLevelMixin, theme_name: LiteralString) -> Json:
    """Return the spec of ``chart`` with a registered theme merged in."""
    # altair annotates PluginEnabler.__exit__ without Optional arguments.
    with alt.theme.enable(theme_name):  # ty: ignore[invalid-context-manager]
        return as_json(chart.to_dict())


def spec_with(chart: alt.TopLevelMixin, config: Config) -> Json:
    """Return the spec of ``chart`` with the theme built from ``config``."""
    with alt.theme.enable("none"):  # ty: ignore[invalid-context-manager]
        spec = as_json(chart.to_dict())
    spec["config"] = {
        **as_json(build_theme(config))["config"],
        **spec.get("config", {}),
    }
    return spec


@functools.cache
def vega_lite_schema() -> Json:
    return load_schema()


def schema_errors(instance: Json, definition: str | None = None) -> list[str]:
    """Validate against the Vega-Lite schema or one of its definitions."""
    schema = vega_lite_schema()
    if definition is not None:
        schema = {
            "$ref": f"#/definitions/{definition}",
            "definitions": schema["definitions"],
        }
    validator = jsonschema.Draft7Validator(schema)
    return [
        "/".join(map(str, error.absolute_path)) + ": " + error.message
        for error in validator.iter_errors(instance)
    ]


def scene(spec: Json) -> list[Json]:
    """Flatten the scenegraph of ``spec`` into items with absolute positions.

    Each item gets the keys ``role`` and ``marktype`` of its mark, ``ax`` and
    ``ay`` for its position relative to the plot origin, and ``axis`` for the
    orientation of the axis it belongs to (if any).
    """
    graph = vlc.vegalite_to_scenegraph(spec, vl_version=VL_VERSION)
    items: list[Json] = []

    def walk(mark: Json, x0: float, y0: float, axis: str | None) -> None:
        for item in mark.get("items", []):
            x = x0 + (item.get("x") or 0)
            y = y0 + (item.get("y") or 0)
            orient = item.get("orient") if mark.get("role") == "axis" else None
            flat = {k: v for k, v in item.items() if k != "items"}
            flat |= {
                "role": mark.get("role"),
                "marktype": mark.get("marktype"),
                "ax": x,
                "ay": y,
                "axis": orient or axis,
            }
            items.append(flat)
            if mark.get("marktype") == "group":
                for child in item.get("items", []):
                    walk(child, x, y, orient or axis)

    walk(graph["scenegraph"], 0.0, 0.0, None)
    return items


def find(items: Iterable[Json], **match: object) -> list[Json]:
    return [
        item
        for item in items
        if all(item.get(key) == value for key, value in match.items())
    ]


def find_one(items: Iterable[Json], **match: object) -> Json:
    found = find(items, **match)
    assert len(found) == 1, f"expected one item matching {match}: {found}"
    return found[0]


def text_top_bottom(item: Json) -> tuple[float, float]:
    """Vertical extent of an unrotated text item."""
    assert not item.get("angle"), "only unrotated text is supported"
    size, y = item["fontSize"], item["ay"]
    match item.get("baseline", "alphabetic"):
        case "top":
            return y, y + size
        case "bottom":
            return y - size, y
        case "middle":
            return y - size / 2, y + size / 2
        case _:
            return y - 0.8 * size, y + 0.2 * size


def plot_size(items: list[Json]) -> tuple[float, float]:
    frame = items[0]
    assert frame["role"] == "frame"
    return frame["width"], frame["height"]


def luminance(color: str) -> float:
    """WCAG relative luminance of a hex or (supported) named colour."""
    hex_color = CSS_COLORS.get(color, color)
    assert re.fullmatch(r"#[0-9a-fA-F]{6}", hex_color), color
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = (
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        for c in channels
    )
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(foreground: str, background: str) -> float:
    high, low = sorted(
        (luminance(foreground), luminance(background)), reverse=True
    )
    return (high + 0.05) / (low + 0.05)


def run_python(code: str) -> str:
    """Run ``code`` in a fresh interpreter and return its stdout."""
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


# Registration -------------------------------------------------------------


def test_import_does_not_enable_a_theme() -> None:
    code = "import altair, camminady_altair_theme; print(altair.theme.active)"
    assert run_python(code) == "default"


@pytest.mark.parametrize("theme_name", THEME_NAMES)
def test_theme_can_be_enabled_without_import(theme_name: str) -> None:
    code = (
        "import sys, altair as alt\n"
        f"alt.theme.enable({theme_name!r})\n"
        "print(alt.theme.active, 'camminady_altair_theme' in sys.modules)"
    )
    assert run_python(code) == f"{theme_name} True"


def test_entry_points_are_declared() -> None:
    declared = {
        ep.name: ep.value
        for ep in entry_points(group="altair.vegalite.v6.theme")
    }
    assert declared["camminady"] == "camminady_altair_theme.theme:camminady"
    assert (
        declared["camminady_dark"]
        == "camminady_altair_theme.theme:camminady_dark"
    )


def test_registered_themes_are_built_from_the_module_configs() -> None:
    assert set(THEME_NAMES) <= set(alt.theme.names())
    assert camminady() == build_theme(theme_module.config)
    assert camminady_dark() == build_theme(theme_module.config_dark)


def test_theme_returns_a_fresh_dict() -> None:
    first = camminady()
    first.setdefault("config", {})["background"] = "red"
    assert camminady().get("config", {}).get("background") == "white"


@pytest.mark.parametrize("config", CONFIGS.values(), ids=CONFIGS.keys())
def test_theme_does_not_share_containers_between_keys(config: Config) -> None:
    # Altair deep-copies the theme before merging the chart's own config into
    # it, which keeps shared references: a container used for two keys would
    # make a user setting for one key leak into the other.
    seen: set[int] = set()

    def visit(node: object) -> None:
        if isinstance(node, dict | list):
            assert id(node) not in seen, f"shared container: {node}"
            seen.add(id(node))
            children = node.values() if isinstance(node, dict) else node
            for child in children:
                visit(child)

    visit(build_theme(config))


def test_user_config_for_one_header_does_not_leak_into_another() -> None:
    chart = (
        base("point")
        .encode(x="x:Q", y="y:Q", column="panel:N")
        .configure_headerColumn(labelPadding=5)
    )
    config = spec_for(chart, "camminady")["config"]
    assert config["headerColumn"]["labelPadding"] == 5
    assert config["headerFacet"]["labelPadding"] != 5


# Schema validity --------------------------------------------------------------


@pytest.mark.parametrize("config", CONFIGS.values(), ids=CONFIGS.keys())
def test_theme_config_is_valid_vega_lite(config: Config) -> None:
    theme = as_json(build_theme(config))
    assert set(theme) == {"config"}
    assert schema_errors(theme["config"], "Config") == []


@pytest.mark.parametrize(
    "invalid",
    [{"view": {"width": 800}}, {"facet": {"color": "red"}}],
    ids=["view.width", "facet.color"],
)
def test_schema_check_rejects_keys_of_the_previous_theme(
    invalid: Json,
) -> None:
    assert schema_errors(invalid, "Config") != []


@pytest.mark.parametrize("theme_name", THEME_NAMES)
@pytest.mark.parametrize("chart_name", GALLERY)
def test_themed_spec_is_valid_and_renders(
    chart_name: str, theme_name: LiteralString
) -> None:
    spec = spec_for(GALLERY[chart_name], theme_name)
    assert schema_errors(spec) == []
    svg = vlc.vegalite_to_svg(spec, vl_version=VL_VERSION)
    assert svg.startswith("<svg")


def test_png_export() -> None:
    spec = spec_for(GALLERY["scatter_legend"], "camminady")
    png = vlc.vegalite_to_png(spec, vl_version=VL_VERSION, scale=1)
    assert png.startswith(b"\x89PNG")


# Accessibility ------------------------------------------------------------


@pytest.mark.parametrize("config", CONFIGS.values(), ids=CONFIGS.keys())
def test_text_meets_wcag_aa_contrast(config: Config) -> None:
    background = config.color_background
    assert contrast(config.color_primary, background) >= 4.5
    assert contrast(config.color_secondary, background) >= 4.5
    assert contrast(config.color_rule, background) >= 3


def test_okabe_ito_palette_is_usable_as_scale_range() -> None:
    chart = base("point").encode(
        color=alt.Color("series:N").scale(range=OKABE_ITO)
    )
    spec = spec_for(chart, "camminady")
    assert spec["encoding"]["color"]["scale"]["range"] == list(OKABE_ITO)
    assert len(set(OKABE_ITO)) == len(OKABE_ITO) == 7


# Layout -------------------------------------------------------------------


@pytest.mark.parametrize("config", CONFIGS.values(), ids=CONFIGS.keys())
@pytest.mark.parametrize("x_field", ["series:N", "x:Q"])
def test_views_use_the_configured_size(config: Config, x_field: str) -> None:
    chart = base("point").encode(x=x_field, y="y:Q")
    assert plot_size(scene(spec_with(chart, config))) == (
        config.width,
        config.height,
    )


@pytest.mark.parametrize("config", CONFIGS.values(), ids=CONFIGS.keys())
def test_top_legend_does_not_overlap_y_title(config: Config) -> None:
    chart = line().encode(
        y=alt.Y("y:Q", title=Y_TITLE),
        color=alt.Color("series:N").legend(orient="top"),
    )
    items = scene(spec_with(chart, config))
    legend = find_one(items, role="legend", marktype="group")
    title_top, _ = text_top_bottom(find_one(items, text=Y_TITLE))
    assert legend["ay"] + legend["height"] < title_top


@pytest.mark.parametrize("config", CONFIGS.values(), ids=CONFIGS.keys())
def test_axis_titles_stay_within_the_plot_width(config: Config) -> None:
    chart = line().encode(
        x=alt.X("x:Q", title=X_TITLE), y=alt.Y("y:Q", title=Y_TITLE)
    )
    items = scene(spec_with(chart, config))
    width, _ = plot_size(items)
    x_title = find_one(items, text=X_TITLE)
    y_title = find_one(items, text=Y_TITLE)
    # Axes are offset by half a pixel to draw crisp lines.
    assert x_title["align"] == "right"
    assert x_title["ax"] == pytest.approx(width, abs=1)
    assert y_title["align"] == "left"
    assert y_title["ax"] == pytest.approx(0, abs=1)
    legend = find_one(items, role="legend", marktype="group")
    assert legend["ax"] > x_title["ax"]


def test_right_y_axis_labels_and_title_sit_outside_the_plot() -> None:
    chart = alt.layer(
        base("line").encode(x="x:Q", y=alt.Y("y:Q", title="left")),
        base("line").encode(x="x:Q", y=alt.Y("x:Q", title="right")),
    ).resolve_scale(y="independent")
    items = scene(spec_with(chart, Config()))
    width, _ = plot_size(items)
    labels = find(items, role="axis-label", axis="right")
    assert labels
    assert all(label["align"] == "left" for label in labels)
    assert all(label["ax"] > width for label in labels)
    title = find_one(items, role="axis-title", text="right")
    assert title["align"] == "right"
    assert title["ax"] == pytest.approx(width, abs=1)


@pytest.mark.parametrize("config", CONFIGS.values(), ids=CONFIGS.keys())
def test_column_headers_do_not_overlap_y_title(config: Config) -> None:
    chart = (
        base("point")
        .encode(x="x:Q", y=alt.Y("y:Q", title=Y_TITLE), column="panel:N")
        .properties(width=200, height=150)
    )
    items = scene(spec_with(chart, config))
    title_top, _ = text_top_bottom(find_one(items, text=Y_TITLE))
    header = find_one(items, text="panel 0")
    _, header_bottom = text_top_bottom(header)
    assert header_bottom < title_top


def test_subtitle_is_themed() -> None:
    config = Config()
    chart = line().properties(title=alt.Title("Title", subtitle="Subtitle"))
    subtitle = find_one(scene(spec_with(chart, config)), text="Subtitle")
    assert subtitle["fill"] == config.color_secondary
    assert subtitle["fontSize"] == config.size_medium


def test_user_header_config_overrides_the_theme() -> None:
    chart = (
        base("line")
        .encode(x="x:Q", y="y:Q", row="series:N")
        .configure_header(labelFontSize=21)
    )
    items = scene(spec_for(chart, "camminady"))
    assert find_one(items, text="series 0")["fontSize"] == 21


def test_background_can_be_made_transparent() -> None:
    chart = line().configure(background="transparent")
    spec = spec_for(chart, "camminady")
    assert spec["config"]["background"] == "transparent"
    # The plot area must not be painted (it used to be filled white).
    frame = scene(spec)[0]
    assert frame["fill"] in (None, "transparent")
