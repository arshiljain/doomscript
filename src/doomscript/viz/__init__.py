"""DoomScript Grammar-of-Graphics Visualization Subsystem."""

from doomscript.viz.spec import (
    PlotSpec,
    AestheticMapping,
    LayerSpec,
    FacetSpec,
    ThemeSpec,
    ScaleSpec,
    LabelSpec,
)
from doomscript.viz.builder import PlotBuilder
from doomscript.viz.explorer import explore_dataset, ExplorationReport
from doomscript.viz.renderer import plot_table, show_plot, save_plot

__all__ = [
    "PlotSpec",
    "AestheticMapping",
    "LayerSpec",
    "FacetSpec",
    "ThemeSpec",
    "ScaleSpec",
    "LabelSpec",
    "PlotBuilder",
    "explore_dataset",
    "ExplorationReport",
    "plot_table",
    "show_plot",
    "save_plot",
]
