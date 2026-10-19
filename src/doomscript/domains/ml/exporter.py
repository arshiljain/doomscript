"""Native Python AST Exporter for Machine Learning domain models."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.ml.spec import ModelSpec


class MLASTExporter(DomainASTExporter):
    """Translates ModelSpec IR into idiomatic scikit-learn Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        if not isinstance(ir, ModelSpec):
            raise TypeError(f"MLASTExporter expects ModelSpec, got {type(ir).__name__}")

        imports: Set[str] = {"pandas", "sklearn"}
        stmts: List[ast.stmt] = []

        algo = ir.algorithm.lower()
        if algo in ("linear_regression", "ols"):
            algo_cls = "LinearRegression"
        elif algo in ("logistic_regression", "classification"):
            algo_cls = "LogisticRegression"
        elif algo in ("decision_tree", "tree"):
            algo_cls = "DecisionTreeClassifier"
        elif algo in ("k_means", "kmeans", "clustering"):
            algo_cls = "KMeans"
        else:
            algo_cls = "RandomForestClassifier"

        # 1. Prepare dataframe and feature matrix extraction
        df_name = f"{var_name}_df"
        stmts.append(
            ast.Assign(
                targets=[ast.Name(id=df_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(value=ast.Name(id="pd", ctx=ast.Load()), attr="DataFrame", ctx=ast.Load()),
                    args=[ast.Name(id=ir.dataset, ctx=ast.Load())],
                    keywords=[],
                ),
            )
        )

        feat_list = ast.List(elts=[ast.Constant(value=f) for f in ir.features], ctx=ast.Load())
        x_name = f"{var_name}_X"
        stmts.append(
            ast.Assign(
                targets=[ast.Name(id=x_name, ctx=ast.Store())],
                value=ast.Subscript(
                    value=ast.Name(id=df_name, ctx=ast.Load()),
                    slice=feat_list,
                    ctx=ast.Load(),
                ),
            )
        )

        if ir.target:
            y_name = f"{var_name}_y"
            stmts.append(
                ast.Assign(
                    targets=[ast.Name(id=y_name, ctx=ast.Store())],
                    value=ast.Subscript(
                        value=ast.Name(id=df_name, ctx=ast.Load()),
                        slice=ast.Constant(value=ir.target),
                        ctx=ast.Load(),
                    ),
                )
            )

        # 1b. Feature scaling if configured
        if ir.scale_features:
            imports.add("sklearn.preprocessing")
            scaler_inst_name = f"{var_name}_scaler"
            stmts.append(
                ast.Assign(
                    targets=[ast.Name(id=scaler_inst_name, ctx=ast.Store())],
                    value=ast.Call(func=ast.Name(id="StandardScaler", ctx=ast.Load()), args=[], keywords=[]),
                )
            )
            stmts.append(
                ast.Assign(
                    targets=[ast.Name(id=x_name, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(value=ast.Name(id=scaler_inst_name, ctx=ast.Load()), attr="fit_transform", ctx=ast.Load()),
                        args=[ast.Name(id=x_name, ctx=ast.Load())],
                        keywords=[],
                    ),
                )
            )

        # 2. Instantiate and fit sklearn model
        model_inst_name = f"{var_name}_model"
        inst_keywords = []
        if ir.seed is not None and algo_cls in ("RandomForestClassifier", "LogisticRegression", "DecisionTreeClassifier", "KMeans"):
            inst_keywords.append(ast.keyword(arg="random_state", value=ast.Constant(value=ir.seed)))
        inst_call = ast.Call(
            func=ast.Name(id=algo_cls, ctx=ast.Load()),
            args=[],
            keywords=inst_keywords,
        )
        stmts.append(ast.Assign(targets=[ast.Name(id=model_inst_name, ctx=ast.Store())], value=inst_call))

        # 3. Fit call
        fit_args = [ast.Name(id=x_name, ctx=ast.Load())]
        if ir.target:
            fit_args.append(ast.Name(id=y_name, ctx=ast.Load()))

        fit_call = ast.Call(
            func=ast.Attribute(value=ast.Name(id=model_inst_name, ctx=ast.Load()), attr="fit", ctx=ast.Load()),
            args=fit_args,
            keywords=[],
        )
        stmts.append(ast.Expr(value=fit_call))

        # 4. Assign model instance to target variable
        stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=ast.Name(id=model_inst_name, ctx=ast.Load())))

        return imports, stmts
