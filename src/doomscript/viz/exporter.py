"""Native Python Code Exporter for Lets-Plot.

Translates PlotSpec IR into clean, idiomatic native Python code
using lets_plot functions (ggplot, aes, geom_*, theme_*, etc.).
"""

from typing import List, Set
from doomscript.viz.spec import PlotSpec


class LetsPlotExporter:
    """Translates PlotSpec IR into idiomatic native Python lets_plot statements."""

    def to_python(self, spec: PlotSpec, var_name: str = "p") -> str:
        imports: Set[str] = {"ggplot", "aes"}
        lines: List[str] = []

        # Data representation
        data_repr = (
            spec.data if isinstance(spec.data, str) else repr(spec.data)
        )

        # Global aes mapping
        aes_pairs = []
        if spec.mapping.x:
            aes_pairs.append(f'x="{spec.mapping.x}"')
        if spec.mapping.y:
            aes_pairs.append(f'y="{spec.mapping.y}"')
        if spec.mapping.color:
            aes_pairs.append(f'color="{spec.mapping.color}"')
        if spec.mapping.fill:
            aes_pairs.append(f'fill="{spec.mapping.fill}"')
        if spec.mapping.size:
            aes_pairs.append(f'size="{spec.mapping.size}"')
        if spec.mapping.shape:
            aes_pairs.append(f'shape="{spec.mapping.shape}"')
        if spec.mapping.alpha:
            aes_pairs.append(f'alpha="{spec.mapping.alpha}"')
        if spec.mapping.group:
            aes_pairs.append(f'group="{spec.mapping.group}"')
        if spec.mapping.slice:
            aes_pairs.append(f'slice="{spec.mapping.slice}"')
        if spec.mapping.value:
            aes_pairs.append(f'weight="{spec.mapping.value}"')

        aes_str = f", aes({', '.join(aes_pairs)})" if aes_pairs else ""
        first_call = f"ggplot({data_repr}{aes_str})"
        chain = [first_call]

        # Layers
        for layer in spec.layers:
            g = layer.geom
            func_name = f"geom_{g}"
            imports.add(func_name)

            param_parts = []
            if layer.stat:
                param_parts.append(f'stat="{layer.stat}"')
            for k, v in layer.params.items():
                param_parts.append(f"{k}={repr(v)}")

            chain.append(f"{func_name}({', '.join(param_parts)})")

        # Facet
        if spec.facet:
            if spec.facet.type == "wrap" and spec.facet.facets:
                imports.add("facet_wrap")
                chain.append(f'facet_wrap(facets="{spec.facet.facets}")')
            elif spec.facet.type == "grid":
                imports.add("facet_grid")
                parts = []
                if spec.facet.col:
                    parts.append(f'x="{spec.facet.col}"')
                if spec.facet.row:
                    parts.append(f'y="{spec.facet.row}"')
                chain.append(f"facet_grid({', '.join(parts)})")

        # Labels
        lab_parts = []
        if spec.labels.title:
            imports.add("ggtitle")
            chain.append(f"ggtitle({repr(spec.labels.title)})")
        if spec.labels.subtitle:
            lab_parts.append(f"subtitle={repr(spec.labels.subtitle)}")
        if spec.labels.caption:
            lab_parts.append(f"caption={repr(spec.labels.caption)}")
        if spec.labels.x:
            imports.add("xlab")
            chain.append(f"xlab({repr(spec.labels.x)})")
        if spec.labels.y:
            imports.add("ylab")
            chain.append(f"ylab({repr(spec.labels.y)})")
        if spec.labels.color:
            lab_parts.append(f"color={repr(spec.labels.color)}")
        if spec.labels.fill:
            lab_parts.append(f"fill={repr(spec.labels.fill)}")

        if lab_parts:
            imports.add("labs")
            chain.append(f"labs({', '.join(lab_parts)})")

        # Theme
        theme_name = spec.theme.name
        if theme_name in ("minimal", "classic", "bw", "light", "void", "grey", "dark"):
            th_func = f"theme_{theme_name}"
            if theme_name == "dark":
                th_func = "theme_minimal"
                imports.add("flavor_darcula")
            imports.add(th_func)
            chain.append(f"{th_func}()")
            if theme_name == "dark":
                chain.append("flavor_darcula()")

        # Scales
        for s in spec.scales:
            if s.target == "color" and s.type == "palette":
                imports.add("scale_color_viridis")
                pal_arg = f'option="{s.palette_name}"' if s.palette_name else ""
                chain.append(f"scale_color_viridis({pal_arg})")
            elif s.target == "fill" and s.type == "palette":
                imports.add("scale_fill_viridis")
                pal_arg = f'option="{s.palette_name}"' if s.palette_name else ""
                chain.append(f"scale_fill_viridis({pal_arg})")
            elif s.target == "x" and s.type == "log":
                imports.add("scale_x_log10")
                chain.append("scale_x_log10()")
            elif s.target == "y" and s.type == "log":
                imports.add("scale_y_log10")
                chain.append("scale_y_log10()")
            elif s.target == "y" and s.type == "reverse":
                imports.add("scale_y_reverse")
                chain.append("scale_y_reverse()")

        sorted_imports = sorted(list(imports))
        import_stmt = f"from lets_plot import {', '.join(sorted_imports)}"

        formatted_chain = f"{var_name} = (" + "\n    + ".join(chain) + "\n)"
        return f"{import_stmt}\n\n{formatted_chain}"
