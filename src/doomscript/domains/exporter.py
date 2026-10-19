"""Domain AST Transformer integrating domain code exporters into native Python AST."""

import ast
from typing import Dict, List, Set, Tuple
from doomscript.domains.registry import get_domain_registry


class DomainASTTransformer(ast.NodeTransformer):
    """Walks the Python AST and transforms domain execution calls into native AST nodes."""

    def __init__(self):
        super().__init__()
        self.collected_imports: Set[str] = set()

    def visit_Assign(self, node: ast.Assign):
        # Check if right-hand side is execute_<domain>_ir('spec_id')
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            func_name = node.value.func.id
            if func_name.startswith("execute_") and func_name.endswith("_ir"):
                domain_name = func_name[len("execute_") : -len("_ir")]
                if node.value.args and isinstance(node.value.args[0], ast.Constant):
                    spec_id = str(node.value.args[0].value)
                    reg = get_domain_registry()
                    spec = reg.get_spec(spec_id)
                    domain = reg.get_domain(domain_name)
                    if spec is not None and domain is not None and domain.exporter is not None:
                        # Extract target variable name
                        target_name = "output"
                        if node.targets and isinstance(node.targets[0], ast.Name):
                            target_name = node.targets[0].id

                        imports, stmts = domain.exporter.to_ast(spec, target_name)
                        self.collected_imports.update(imports)
                        return stmts
        return self.generic_visit(node)


def transform_domains_ast(py_ast: ast.Module) -> ast.Module:
    """Transforms all domain IR calls in py_ast using their registered DomainASTExporter."""
    transformer = DomainASTTransformer()
    new_ast = transformer.visit(py_ast)
    ast.fix_missing_locations(new_ast)

    # Insert collected imports at top of module
    top_imports: List[ast.stmt] = []
    if "pandas" in transformer.collected_imports:
        top_imports.append(ast.Import(names=[ast.alias(name="pandas", asname="pd")]))
    if "numpy" in transformer.collected_imports:
        top_imports.append(ast.Import(names=[ast.alias(name="numpy", asname="np")]))
    if "sklearn" in transformer.collected_imports:
        top_imports.append(ast.Import(names=[ast.alias(name="sklearn")]))
    if "sqlite3" in transformer.collected_imports:
        top_imports.append(ast.Import(names=[ast.alias(name="sqlite3")]))
    if "requests" in transformer.collected_imports:
        top_imports.append(ast.Import(names=[ast.alias(name="requests")]))
    if "urllib.request" in transformer.collected_imports:
        top_imports.append(ast.Import(names=[ast.alias(name="urllib.request")]))

    if "PIL.Image" in transformer.collected_imports:
        top_imports.append(ast.ImportFrom(module="PIL", names=[ast.alias(name="Image")], level=0))
    if "bs4" in transformer.collected_imports:
        top_imports.append(ast.ImportFrom(module="bs4", names=[ast.alias(name="BeautifulSoup")], level=0))

    # Other imports
    for imp in transformer.collected_imports - {"pandas", "numpy", "sklearn", "sqlite3", "requests", "urllib.request", "PIL.Image", "bs4"}:
        top_imports.append(ast.Import(names=[ast.alias(name=imp)]))

    if top_imports:
        new_ast.body = top_imports + new_ast.body

    return new_ast
