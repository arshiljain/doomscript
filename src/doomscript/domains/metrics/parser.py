"""Metrics Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class MetricsDomainParser(DomainParser):
    """Parses spoken-English metrics, counters, histograms, and Prometheus statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # create counter <name> into <target>
        m_cnt = re.match(
            r"^create\s+counter\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cnt:
            name, target = m_cnt.group(1).strip(), m_cnt.group(2).strip()
            if not (name.startswith('"') or name.startswith("'") or name.isidentifier()):
                name = f'"{name}"'
            return f"set {target} to metrics_counter({name})"

        # create gauge <name> into <target>
        m_g = re.match(
            r"^create\s+gauge\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_g:
            name, target = m_g.group(1).strip(), m_g.group(2).strip()
            if not (name.startswith('"') or name.startswith("'") or name.isidentifier()):
                name = f'"{name}"'
            return f"set {target} to metrics_gauge({name})"

        # export openmetrics [metrics] into <target>
        m_exp = re.match(
            r"^export\s+(?:openmetrics|domain\s+metrics)(?:\s+metrics)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_exp:
            target = m_exp.group(1).strip()
            return f"set {target} to metrics_export_openmetrics()"

        # calculate mann whitney u test between <s1> and <s2> into <target>
        m_mwu = re.match(
            r"^calculate\s+mann\s+whitney\s+u\s+test\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mwu:
            s1, s2, target = m_mwu.group(1).strip(), m_mwu.group(2).strip(), m_mwu.group(3).strip()
            return f"set {target} to metrics_mann_whitney_u({s1}, {s2})"

        # calculate kolmogorov smirnov test between <s1> and <s2> into <target>
        m_ks = re.match(
            r"^calculate\s+kolmogorov\s+smirnov\s+test\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ks:
            s1, s2, target = m_ks.group(1).strip(), m_ks.group(2).strip(), m_ks.group(3).strip()
            return f"set {target} to metrics_kolmogorov_smirnov_2samp({s1}, {s2})"

        # compute / calculate kernel density estimation for <data> [with bandwidth <h>] into <target>
        m_kde = re.match(
            r"^(?:calculate|compute)\s+kernel\s+density\s+estimation\s+for\s+(.+?)(?:\s+with\s+bandwidth\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_kde:
            data = m_kde.group(1).strip()
            bw = m_kde.group(2).strip() if m_kde.group(2) else "None"
            target = m_kde.group(3).strip()
            return f"set {target} to metrics_kde_create({data}, bandwidth={bw})"

        # evaluate kde <kde> at points <pts> into <target>
        m_kde_ev = re.match(
            r"^evaluate\s+kde\s+(.+?)\s+at\s+points\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_kde_ev:
            kde, pts, target = m_kde_ev.group(1).strip(), m_kde_ev.group(2).strip(), m_kde_ev.group(3).strip()
            return f"set {target} to metrics_kde_evaluate({kde}, {pts})"

        # calculate wasserstein distance between <u> and <v> into <target>
        m_w1 = re.match(
            r"^calculate\s+wasserstein\s+distance\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_w1:
            u, v, target = m_w1.group(1).strip(), m_w1.group(2).strip(), m_w1.group(3).strip()
            return f"set {target} to metrics_wasserstein_distance_1d({u}, {v})"

        # calculate multiclass roc auc true <y_true> probs <y_probs> classes <k> into <target>
        m_auc = re.match(
            r"^calculate\s+multiclass\s+roc\s+auc\s+true\s+(.+?)\s+probs\s+(.+?)\s+classes\s+(\d+)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_auc:
            y_t, probs, k, target = m_auc.group(1).strip(), m_auc.group(2).strip(), m_auc.group(3).strip(), m_auc.group(4).strip()
            return f"set {target} to metrics_multiclass_roc_auc({y_t}, {probs}, {k})"

        # calculate confusion metrics actual <y_true> predicted <y_pred> into <target>
        m_cm = re.match(
            r"^calculate\s+confusion\s+metrics\s+actual\s+(.+?)\s+predicted\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cm:
            y_t, y_p, target = m_cm.group(1).strip(), m_cm.group(2).strip(), m_cm.group(3).strip()
            return f"set {target} to metrics_confusion_matrix_multiclass({y_t}, {y_p})"

        # calculate precision recall ap actual <y_true> scores <scores> into <target>
        m_ap = re.match(
            r"^calculate\s+precision\s+recall\s+ap\s+actual\s+(.+?)\s+scores\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ap:
            y_t, scores, target = m_ap.group(1).strip(), m_ap.group(2).strip(), m_ap.group(3).strip()
            return f"set {target} to metrics_precision_recall_ap({y_t}, {scores})"

        # calculate <p>th percentile of <values> into <target>
        m_pct = re.match(
            r"^calculate\s+(\d+(?:\.\d+)?)(?:th|st|nd|rd)?\s+percentile\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pct:
            p_val, vals, target = m_pct.group(1).strip(), m_pct.group(2).strip(), m_pct.group(3).strip()
            return f"set {target} to metrics_calculate_percentile({vals}, {p_val})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Metrics domain does not define declarative blocks")
