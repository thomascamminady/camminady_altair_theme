"""Minimal Altair themes: ``"camminady"`` and ``"camminady_dark"``.

Enable a theme with ``alt.theme.enable("camminady")``. Importing this package
registers the themes but does not enable them.

.. include:: ../../README.md
   :start-after: <!-- docs-start -->
"""

from importlib.metadata import version

from camminady_altair_theme.theme import (
    OKABE_ITO,
    Config,
    build_theme,
    camminady,
    camminady_dark,
)

__all__ = [
    "OKABE_ITO",
    "Config",
    "build_theme",
    "camminady",
    "camminady_dark",
]
__version__ = version("camminady-altair-theme")
