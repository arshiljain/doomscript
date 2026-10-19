"""Native Python AST Exporter for NLP & Text Analytics domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.nlp.spec import (
    NLPCleanSpec,
    NLPTokenizeSpec,
    NLPNgramSpec,
    NLPSentimentSpec,
    NLPTfidfSpec,
    NLPEntitiesSpec,
)


class NLPASTExporter(DomainASTExporter):
    """Translates NLP Domain IR into Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        imports: Set[str] = {"re"}
        stmts: List[ast.stmt] = []

        if isinstance(ir, NLPCleanSpec):
            # target = re.sub(r'[^\w\s]', ' ', text.lower()).strip()
            call_node = ast.Call(
                func=ast.Name(id="clean_text", ctx=ast.Load()),
                args=[ast.Name(id=ir.text_expr, ctx=ast.Load())],
                keywords=[ast.keyword(arg="remove_stopwords", value=ast.Constant(value=ir.remove_stopwords))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, NLPTokenizeSpec):
            call_node = ast.Call(
                func=ast.Name(id="tokenize_text", ctx=ast.Load()),
                args=[ast.Name(id=ir.text_expr, ctx=ast.Load())],
                keywords=[ast.keyword(arg="mode", value=ast.Constant(value=ir.mode))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, NLPTfidfSpec):
            imports.add("sklearn.feature_extraction.text")
            # vec = TfidfVectorizer(...)
            # target = {"matrix": vec.fit_transform(corpus).toarray().tolist(), "vocabulary": vec.get_feature_names_out().tolist()}
            call_node = ast.Call(
                func=ast.Name(id="calculate_tfidf", ctx=ast.Load()),
                args=[ast.Name(id=ir.corpus_var, ctx=ast.Load())],
                keywords=(
                    [ast.keyword(arg="max_features", value=ast.Constant(value=ir.max_features))]
                    if ir.max_features
                    else []
                ),
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, NLPSentimentSpec):
            call_node = ast.Call(
                func=ast.Name(id="analyze_sentiment", ctx=ast.Load()),
                args=[ast.Name(id=ir.text_expr, ctx=ast.Load())],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, NLPNgramSpec):
            call_node = ast.Call(
                func=ast.Name(id="extract_ngrams", ctx=ast.Load()),
                args=[ast.Name(id=ir.text_expr, ctx=ast.Load())],
                keywords=[ast.keyword(arg="n", value=ast.Constant(value=ir.n))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, NLPEntitiesSpec):
            call_node = ast.Call(
                func=ast.Name(id="extract_entities", ctx=ast.Load()),
                args=[ast.Name(id=ir.text_expr, ctx=ast.Load())],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        return imports, stmts
