"""Render the example charts shown in the README."""

from pathlib import Path

import altair as alt
from vega_datasets import data

ASSETS = Path(__file__).parent / "assets"


def main() -> None:
    # The theme is found through its entry point; no import is needed.
    alt.theme.enable("camminady")
    base = (
        alt.Chart(data.stocks())
        .mark_line(strokeWidth=3)
        .encode(
            x="date:T",
            y="price:Q",
            color="symbol:N",
            strokeDash="symbol:N",
        )
        .properties(title="This is the chart title")
    )
    base.save(ASSETS / "single_chart.png", scale_factor=4)
    base.encode(row="symbol:N").properties(height=100).save(
        ASSETS / "facet_chart.png", scale_factor=4
    )


if __name__ == "__main__":
    main()
