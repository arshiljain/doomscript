"""Independent Domain Parser for Machine Learning language constructs."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.ml.spec import ModelSpec


class MLDomainParser(DomainParser):
    """Independent parser for Machine Learning syntax (inspect, train, evaluate, predict, model blocks)."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        # inspect model <name> [into <target>]
        m = re.match(
            r"^inspect\s+model\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            model_name = m.group(1)
            target = m.group(2) or "model_inspection"
            return f"set {target} to inspect_model({model_name})"

        # summary of model <name> [into <target>]
        m2 = re.match(
            r"^summary\s+of\s+(?:model\s+)?([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m2:
            model_name = m2.group(1)
            target = m2.group(2) or "model_summary"
            return f"set {target} to inspect_model({model_name})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        # train <model_name>
        train_m = re.match(r"^train\s+([A-Za-z_]\w*)\s*$", line.strip(), re.IGNORECASE)
        if train_m:
            model_name = train_m.group(1)
            return f"train_model({model_name})"

        # evaluate <model_name> [into <target>]
        eval_m = re.match(
            r"^evaluate\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if eval_m:
            model_name = eval_m.group(1)
            target = eval_m.group(2) or f"{model_name}_eval"
            return f"set {target} to evaluate_model({model_name})"

        # predict with <model_name> on <features> into <target>
        pred_m = re.match(
            r"^predict\s+with\s+([A-Za-z_]\w*)\s+on\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if pred_m:
            model_name = pred_m.group(1)
            data_var = pred_m.group(2)
            target = pred_m.group(3)
            return f"set {target} to predict_model({model_name}, {data_var})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[ModelSpec, str]:
        # model <name> from <dataset>:
        m = re.match(
            r"^model\s+([A-Za-z_]\w*)\s+from\s+([A-Za-z_]\w*):?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid ML model header: {header}")

        model_name = m.group(1)
        dataset = m.group(2)

        spec = ModelSpec(name=model_name, dataset=dataset, target_var=model_name)

        for l_no, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # target: <col>
            tgt_m = re.match(r"^target\s*:\s*[\"']?([A-Za-z_]\w*)[\"']?$", line, re.IGNORECASE)
            if tgt_m:
                spec.target = tgt_m.group(1)
                continue

            # features: <c1>, <c2>, ...
            feat_m = re.match(r"^features\s*:\s*(.+)$", line, re.IGNORECASE)
            if feat_m:
                raw_feats = feat_m.group(1).split(",")
                spec.features = [f.strip().strip("\"'") for f in raw_feats if f.strip()]
                continue

            # algorithm: <algo>
            algo_m = re.match(r"^algorithm\s*:\s*([A-Za-z_]\w*)$", line, re.IGNORECASE)
            if algo_m:
                spec.algorithm = algo_m.group(1).lower()
                continue

            # split: 80% training, 20% testing
            split_m = re.match(
                r"^split\s*:\s*(\d+)%?\s*(?:training|train)?\s*,\s*(\d+)%?\s*(?:testing|test)?",
                line,
                re.IGNORECASE,
            )
            if split_m:
                train_p = float(split_m.group(1)) / 100.0
                test_p = float(split_m.group(2)) / 100.0
                spec.split_train = train_p
                spec.split_test = test_p
                continue

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"Model validation error for '{model_name}': {'; '.join(errors)}")

        return spec, model_name
