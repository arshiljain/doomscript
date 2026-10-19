"""Lets-Plot Backend Renderer.

Lazily bridges PlotSpec IR to lets_plot objects and exports to HTML, SVG, PNG, and PDF.
"""

import os
from typing import Optional
from doomscript.viz.spec import PlotSpec


class LetsPlotRenderer:
    """Renderer converting PlotSpec into active Lets-Plot visualizations."""

    @staticmethod
    def _get_lets_plot():
        try:
            import lets_plot as lp

            return lp
        except ImportError:
            raise ImportError(
                "Lets-Plot is required to render or export visualizations.\n"
                "To install it, run:\n"
                "    pip install doomscript[viz]\n"
                "or:\n"
                "    pip install lets-plot"
            )

    @classmethod
    def to_lets_plot(cls, spec: PlotSpec):
        """Builds a lets_plot.ggplot object from the given PlotSpec."""
        lp = cls._get_lets_plot()

        # Build aes mappings
        aes_kwargs = {}
        if spec.mapping.x:
            aes_kwargs["x"] = spec.mapping.x
        if spec.mapping.y:
            aes_kwargs["y"] = spec.mapping.y
        if spec.mapping.color:
            aes_kwargs["color"] = spec.mapping.color
        if spec.mapping.fill:
            aes_kwargs["fill"] = spec.mapping.fill
        if spec.mapping.size:
            aes_kwargs["size"] = spec.mapping.size
        if spec.mapping.shape:
            aes_kwargs["shape"] = spec.mapping.shape
        if spec.mapping.alpha:
            aes_kwargs["alpha"] = spec.mapping.alpha
        if spec.mapping.group:
            aes_kwargs["group"] = spec.mapping.group
        if spec.mapping.weight:
            aes_kwargs["weight"] = spec.mapping.weight
        if spec.mapping.slice:
            aes_kwargs["slice"] = spec.mapping.slice
        if spec.mapping.value:
            # Lets-Plot pie uses 2 values or weight
            aes_kwargs["weight"] = spec.mapping.value

        fig = lp.ggplot(spec.data)
        if aes_kwargs:
            fig += lp.aes(**aes_kwargs)

        # Add layers
        for layer in spec.layers:
            geom = layer.geom
            params = dict(layer.params)
            geom_func = getattr(lp, f"geom_{geom}", None)

            if geom == "point":
                geom_func = lp.geom_point
            elif geom == "line":
                geom_func = lp.geom_line
            elif geom == "bar":
                geom_func = lp.geom_bar
                if layer.stat:
                    params["stat"] = layer.stat
            elif geom == "histogram":
                geom_func = lp.geom_histogram
                if layer.stat:
                    params["stat"] = layer.stat
            elif geom == "density":
                geom_func = lp.geom_density
            elif geom == "boxplot":
                geom_func = lp.geom_boxplot
            elif geom == "violin":
                geom_func = lp.geom_violin
            elif geom == "tile":
                geom_func = lp.geom_tile
            elif geom == "pie":
                geom_func = lp.geom_pie
                if layer.stat:
                    params["stat"] = layer.stat
            elif geom == "area":
                geom_func = lp.geom_area
            elif geom == "smooth":
                geom_func = lp.geom_smooth

            if geom_func is not None:
                fig += geom_func(**params)

        # Facets
        if spec.facet:
            if spec.facet.type == "wrap" and spec.facet.facets:
                fig += lp.facet_wrap(facets=spec.facet.facets, scales=spec.facet.scales)
            elif spec.facet.type == "grid":
                fig += lp.facet_grid(
                    x=spec.facet.col, y=spec.facet.row, scales=spec.facet.scales
                )

        # Labels
        lab_kwargs = {}
        if spec.labels.title:
            lab_kwargs["title"] = spec.labels.title
        if spec.labels.subtitle:
            lab_kwargs["subtitle"] = spec.labels.subtitle
        if spec.labels.caption:
            lab_kwargs["caption"] = spec.labels.caption
        if spec.labels.x:
            lab_kwargs["x"] = spec.labels.x
        if spec.labels.y:
            lab_kwargs["y"] = spec.labels.y
        if spec.labels.color:
            lab_kwargs["color"] = spec.labels.color
        if spec.labels.fill:
            lab_kwargs["fill"] = spec.labels.fill

        if lab_kwargs:
            fig += lp.labs(**lab_kwargs)

        # Theme
        theme_name = spec.theme.name
        if theme_name == "minimal":
            fig += lp.theme_minimal()
        elif theme_name == "classic":
            fig += lp.theme_classic()
        elif theme_name == "bw":
            fig += lp.theme_bw()
        elif theme_name == "light":
            fig += lp.theme_light()
        elif theme_name == "void":
            fig += lp.theme_void()
        elif theme_name in ("grey", "gray"):
            fig += lp.theme_grey()

        if spec.theme.dark_mode or theme_name == "dark":
            if hasattr(lp, "flavor_darcula"):
                fig += lp.flavor_darcula()

        # Scales
        for s in spec.scales:
            if s.target == "color" and s.type == "palette":
                fig += lp.scale_color_viridis(option=s.palette_name or "viridis")
            elif s.target == "fill" and s.type == "palette":
                fig += lp.scale_fill_viridis(option=s.palette_name or "viridis")
            elif s.target == "x" and s.type == "log":
                fig += lp.scale_x_log10()
            elif s.target == "y" and s.type == "log":
                fig += lp.scale_y_log10()
            elif s.target == "y" and s.type == "reverse":
                fig += lp.scale_y_reverse()

        # Annotations
        for ann in spec.annotations:
            ann_kw = {"label": ann.text, "x": ann.x, "y": ann.y}
            if ann.color is not None:
                ann_kw["color"] = ann.color
            if ann.size is not None:
                ann_kw["size"] = ann.size
            if ann.alpha is not None:
                ann_kw["alpha"] = ann.alpha
            fig += lp.geom_text(**ann_kw)

        return fig

    @classmethod
    def to_html(cls, spec: PlotSpec) -> str:
        """Generates standalone HTML string for the visualization."""
        fig = cls.to_lets_plot(spec)
        return fig.to_html()

    @classmethod
    def save(
        cls,
        spec: PlotSpec,
        path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        dpi: Optional[int] = None,
    ):
        """Saves visualization to HTML, PNG, SVG, or PDF."""
        lp = cls._get_lets_plot()
        fig = cls.to_lets_plot(spec)

        abs_path = os.path.abspath(path)
        out_dir = os.path.dirname(abs_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        ext = os.path.splitext(abs_path)[1].lower()
        if ext == ".html":
            html_content = fig.to_html()
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return abs_path

        # Static export via ggsave
        filename = os.path.basename(abs_path)
        save_kwargs = {}
        if width is not None:
            save_kwargs["w"] = width
        if height is not None:
            save_kwargs["h"] = height
        if dpi is not None:
            save_kwargs["dpi"] = dpi

        try:
            lp.ggsave(fig, filename=filename, path=out_dir, **save_kwargs)
            return abs_path
        except Exception as e:
            msg = str(e)
            if "pypng" in msg.lower() or "cairo" in msg.lower():
                raise RuntimeError(
                    f"Exporting to {ext} requires additional export libraries.\n"
                    f"Try: pip install pypng\nDetails: {msg}"
                )
            raise

    @classmethod
    def show(cls, spec: PlotSpec):
        """Shows the plot in active display environment."""
        fig = cls.to_lets_plot(spec)
        return fig.show()
