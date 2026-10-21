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
            r"^summary\s+of\s+model\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m2:
            model_name = m2.group(1)
            target = m2.group(2) or "model_summary"
            return f"set {target} to inspect_model({model_name})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        # train model on <dataset> predicting <target_col> using <algo> into <target_var>
        m_train_spoken = re.match(
            r"^train\s+model\s+on\s+([A-Za-z_]\w*)\s+predicting\s+[\"']?([A-Za-z_]\w*)[\"']?\s+using\s+([A-Za-z_]\w*)(?:\s+features\s+\[(.*?)\])?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_train_spoken:
            dataset = m_train_spoken.group(1)
            target_col = m_train_spoken.group(2)
            algo = m_train_spoken.group(3)
            feats_raw = m_train_spoken.group(4)
            target_var = m_train_spoken.group(5)
            feats_arg = f"{[f.strip().strip(chr(34)).strip(chr(39)) for f in feats_raw.split(',') if f.strip()]}" if feats_raw else "None"
            return f'set {target_var} to train_direct_model("{algo}", {dataset}, "{target_col}", {feats_arg})'

        # train <algo> on <dataset> predicting <target_col> [features <f1, f2>] into <target_var>
        train_direct_m = re.match(
            r"^train\s+([A-Za-z_]\w*)\s+on\s+([A-Za-z_]\w*)\s+predicting\s+[\"']?([A-Za-z_]\w*)[\"']?(?:\s+features\s+\[(.*?)\])?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if train_direct_m:
            algo = train_direct_m.group(1)
            dataset = train_direct_m.group(2)
            target_col = train_direct_m.group(3)
            feats_raw = train_direct_m.group(4)
            target_var = train_direct_m.group(5)
            if feats_raw:
                feats_list = [f.strip().strip("\"'") for f in feats_raw.split(",") if f.strip()]
                feats_arg = f'{feats_list}'
            else:
                feats_arg = "None"
            return f'set {target_var} to train_direct_model("{algo}", {dataset}, "{target_col}", {feats_arg})'

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

        # predict [with] <model_name> on <features> into <target>
        pred_m = re.match(
            r"^predict(?:\s+with)?\s+([A-Za-z_]\w*)\s+on\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if pred_m:
            model_name = pred_m.group(1)
            data_var = pred_m.group(2)
            target = pred_m.group(3)
            return f"set {target} to predict_model({model_name}, {data_var})"

        # predict classes for <data> with model <model> into <target>
        pred_cls_m = re.match(
            r"^predict(?:\s+classes)?\s+(?:for|on)\s+(.+?)\s+with\s+(?:model\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if pred_cls_m:
            data_var = pred_cls_m.group(1).strip()
            model_var = pred_cls_m.group(2).strip()
            target = pred_cls_m.group(3).strip()
            return f"set {target} to predict_model({model_var}, {data_var})"

        # accuracy / score of <preds> against <actuals> into <target>
        acc_m = re.match(
            r"^(?:accuracy|score)\s+of\s+(.+?)\s+against\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if acc_m:
            preds_expr = acc_m.group(1).strip()
            actuals_expr = acc_m.group(2).strip()
            target_var = acc_m.group(3).strip()
            return f"set {target_var} to accuracy_score_fn({preds_expr}, {actuals_expr})"

        # cross validate <model_name> [with <N> folds] [into <target>]
        cv_m = re.match(
            r"^cross\s+validate\s+([A-Za-z_]\w*)(?:\s+with\s+(\d+)\s+folds?)?(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if cv_m:
            model_name = cv_m.group(1)
            folds = int(cv_m.group(2)) if cv_m.group(2) else 5
            target = cv_m.group(3) or f"{model_name}_cv"
            return f"set {target} to cross_validate_model({model_name}, folds={folds})"

        # save model <model_name> to <path>
        save_m = re.match(
            r"^save\s+model\s+([A-Za-z_]\w*)\s+to\s+(.+)$",
            line.strip(),
            re.IGNORECASE,
        )
        if save_m:
            model_name = save_m.group(1)
            path = save_m.group(2).strip()
            return f"save_model({model_name}, {path})"

        # load model from <path> into <target>
        load_m = re.match(
            r"^load\s+model\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if load_m:
            path = load_m.group(1).strip()
            target = load_m.group(2).strip()
            return f"set {target} to load_model({path})"

        # split data <data> into train and test with test_size <ts> into <target>
        m_split = re.match(
            r"^split\s+data\s+(.+?)\s+into\s+train\s+and\s+test\s+with\s+test_size\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_split:
            data_var, ts, target = m_split.group(1), m_split.group(2), m_split.group(3)
            return f"set {target} to ml_split_data({data_var}, test_size={ts})"

        # confusion matrix of <actuals> and <preds> into <target>
        m_cm = re.match(
            r"^confusion\s+matrix\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_cm:
            actuals, preds, target = m_cm.group(1), m_cm.group(2), m_cm.group(3)
            return f"set {target} to ml_confusion_matrix({actuals}, {preds})"

        # classification metrics for <actuals> and <preds> into <target>
        m_cmet = re.match(
            r"^classification\s+metrics\s+for\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_cmet:
            actuals, preds, target = m_cmet.group(1), m_cmet.group(2), m_cmet.group(3)
            return f"set {target} to ml_classification_metrics({actuals}, {preds})"

        # roc auc score of <actuals> and <probs> into <target>
        m_auc = re.match(
            r"^roc\s+auc\s+score\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_auc:
            actuals, probs, target = m_auc.group(1), m_auc.group(2), m_auc.group(3)
            return f"set {target} to ml_roc_auc_score({actuals}, {probs})"

        # mean squared error between <actuals> and <preds> into <target>
        m_mse = re.match(
            r"^mean\s+squared\s+error\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_mse:
            actuals, preds, target = m_mse.group(1), m_mse.group(2), m_mse.group(3)
            return f"set {target} to ml_mean_squared_error({actuals}, {preds})"

        # r2 score between <actuals> and <preds> into <target>
        m_r2 = re.match(
            r"^r2\s+score\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_r2:
            actuals, preds, target = m_r2.group(1), m_r2.group(2), m_r2.group(3)
            return f"set {target} to ml_r2_score({actuals}, {preds})"

        # one-hot encode column <col> in <df> into <target>
        m_ohe = re.match(
            r"^one-hot\s+encode\s+column\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_ohe:
            col, df, target = m_ohe.group(1), m_ohe.group(2), m_ohe.group(3)
            return f"set {target} to ml_one_hot_encode({df}, {col})"

        # 350-Expansion ML Operations
        # train knn classifier with features <X> and labels <y> [and neighbors <k>] into <target>
        knn_feat_m = re.match(
            r"^train\s+knn\s+classifier\s+with\s+features\s+(.+?)\s+and\s+labels\s+(.+?)(?:\s+and\s+neighbors\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if knn_feat_m:
            x_var = knn_feat_m.group(1).strip()
            y_var = knn_feat_m.group(2).strip()
            k_val = knn_feat_m.group(3).strip() if knn_feat_m.group(3) else "3"
            target = knn_feat_m.group(4).strip()
            return f"set {target} to ml_train_knn_classifier({x_var}, {y_var}, k={k_val})"

        knn_m = re.match(
            r"^train\s+knn\s+classifier\s+on\s+([A-Za-z_]\w*)\s+predicting\s+(.+?)(?:\s+with\s+(.+?)\s+neighbors)?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if knn_m:
            data_var, tgt_col = knn_m.group(1).strip(), knn_m.group(2).strip()
            k_val = knn_m.group(3).strip() if knn_m.group(3) else "3"
            target = knn_m.group(4).strip()
            return f"set {target} to ml_knn_classifier({data_var}, {tgt_col}, k={k_val})"

        stump_m = re.match(
            r"^fit\s+decision\s+stump\s+on\s+([A-Za-z_]\w*)\s+predicting\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if stump_m:
            data_var, tgt_col, target = stump_m.group(1).strip(), stump_m.group(2).strip(), stump_m.group(3).strip()
            return f"set {target} to ml_decision_stump({data_var}, {tgt_col})"

        gnb_m = re.match(
            r"^train\s+gaussian\s+naive\s+bayes\s+on\s+([A-Za-z_]\w*)\s+predicting\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if gnb_m:
            data_var, tgt_col, target = gnb_m.group(1).strip(), gnb_m.group(2).strip(), gnb_m.group(3).strip()
            return f"set {target} to ml_gaussian_naive_bayes({data_var}, {tgt_col})"

        bnb_m = re.match(
            r"^train\s+bernoulli\s+naive\s+bayes\s+on\s+([A-Za-z_]\w*)\s+predicting\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if bnb_m:
            data_var, tgt_col, target = bnb_m.group(1).strip(), bnb_m.group(2).strip(), bnb_m.group(3).strip()
            return f"set {target} to ml_bernoulli_naive_bayes({data_var}, {tgt_col})"

        km_m = re.match(
            r"^cluster\s+([A-Za-z_]\w*)\s+with\s+kmeans\s+into\s+(.+?)\s+clusters\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if km_m:
            data_var, k_val, target = km_m.group(1).strip(), km_m.group(2).strip(), km_m.group(3).strip()
            return f"set {target} to ml_kmeans_clustering({data_var}, k={k_val})"

        pca_m = re.match(
            r"^reduce\s+dimensionality\s+of\s+([A-Za-z_]\w*)\s+using\s+pca\s+to\s+(.+?)\s+components\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if pca_m:
            data_var, n_comp, target = pca_m.group(1).strip(), pca_m.group(2).strip(), pca_m.group(3).strip()
            return f"set {target} to ml_pca_transform({data_var}, n_components={n_comp})"

        logloss_m = re.match(
            r"^(?:calculate|compute)\s+log\s+loss\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if logloss_m:
            y_t, y_p, target = logloss_m.group(1).strip(), logloss_m.group(2).strip(), logloss_m.group(3).strip()
            return f"set {target} to ml_log_loss({y_t}, {y_p})"

        brier_m = re.match(
            r"^(?:calculate|compute)\s+brier\s+score\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if brier_m:
            y_t, y_p, target = brier_m.group(1).strip(), brier_m.group(2).strip(), brier_m.group(3).strip()
            return f"set {target} to ml_brier_score({y_t}, {y_p})"

        f1_m = re.match(
            r"^(?:compute|calculate)\s+f1\s+score\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if f1_m:
            y_t, y_p, target = f1_m.group(1).strip(), f1_m.group(2).strip(), f1_m.group(3).strip()
            return f"set {target} to ml_f1_score({y_t}, {y_p})"

        pr_m = re.match(
            r"^(?:calculate|compute)\s+precision\s+and\s+recall\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if pr_m:
            y_t, y_p, target = pr_m.group(1).strip(), pr_m.group(2).strip(), pr_m.group(3).strip()
            return f"set {target} to ml_precision_recall({y_t}, {y_p})"

        poly_m = re.match(
            r"^generate\s+polynomial\s+features\s+for\s+([A-Za-z_]\w*)(?:\s+with\s+degree\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if poly_m:
            data_var = poly_m.group(1).strip()
            deg = poly_m.group(2).strip() if poly_m.group(2) else "2"
            target = poly_m.group(3).strip()
            return f"set {target} to ml_polynomial_features({data_var}, degree={deg})"

        tenc_m = re.match(
            r"^target\s+encode\s+column\s+(.+?)\s+using\s+(.+?)\s+in\s+([A-Za-z_]\w*)(?:\s+with\s+smoothing\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if tenc_m:
            cat_col, tgt_col, data_var = tenc_m.group(1).strip(), tenc_m.group(2).strip(), tenc_m.group(3).strip()
            smooth = tenc_m.group(4).strip() if tenc_m.group(4) else "1.0"
            target = tenc_m.group(5).strip()
            return f"set {target} to ml_target_encode({data_var}, {cat_col}, {tgt_col}, smoothing={smooth})"

        lr_m = re.match(
            r"^cosine\s+decay\s+learning\s+rate\s+from\s+(.+?)\s+at\s+step\s+(.+?)\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if lr_m:
            init_lr, step, tot, target = lr_m.group(1).strip(), lr_m.group(2).strip(), lr_m.group(3).strip(), lr_m.group(4).strip()
            return f"set {target} to ml_cosine_decay_lr({init_lr}, {step}, {tot})"

        split3_m = re.match(
            r"^split\s+([A-Za-z_]\w*)\s+into\s+train\s+val\s+test(?:\s+with\s+ratios\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if split3_m:
            data_var = split3_m.group(1).strip()
            target = split3_m.group(3).strip()
            return f"set {target} to ml_train_val_test_split({data_var})"

        ano_m = re.match(
            r"^(?:calculate|compute)\s+anomaly\s+scores\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if ano_m:
            data_var, target = ano_m.group(1).strip(), ano_m.group(2).strip()
            return f"set {target} to ml_one_class_anomaly_score({data_var})"

        sil_m = re.match(
            r"^(?:calculate|compute)\s+silhouette\s+score\s+for\s+([A-Za-z_]\w*)\s+with\s+labels\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if sil_m:
            data_var, lbls, target = sil_m.group(1).strip(), sil_m.group(2).strip(), sil_m.group(3).strip()
            return f"set {target} to ml_silhouette_score_sample({data_var}, {lbls})"

        hinge_m = re.match(
            r"^(?:calculate|compute)\s+hinge\s+loss\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if hinge_m:
            y_t, y_s, target = hinge_m.group(1).strip(), hinge_m.group(2).strip(), hinge_m.group(3).strip()
            return f"set {target} to ml_hinge_loss({y_t}, {y_s})"

        lc_m = re.match(
            r"^(?:calculate|compute)\s+learning\s+curve\s+points\s+for\s+(.+?)\s+on\s+([A-Za-z_]\w*)\s+predicting\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if lc_m:
            model, data_var, tgt_col, target = lc_m.group(1).strip(), lc_m.group(2).strip(), lc_m.group(3).strip(), lc_m.group(4).strip()
            return f"set {target} to ml_learning_curve_points({model}, {data_var}, {tgt_col})"

        ema_m = re.match(
            r"^exponential\s+moving\s+average\s+of\s+weights\s+(.+?)(?:\s+with\s+decay\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if ema_m:
            hist = ema_m.group(1).strip()
            decay = ema_m.group(2).strip() if ema_m.group(2) else "0.99"
            target = ema_m.group(3).strip()
            return f"set {target} to ml_exponential_moving_average_weights({hist}, decay={decay})"

        clipg_m = re.match(
            r"^clip\s+gradients\s+(.+?)\s+by\s+norm\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if clipg_m:
            grads, max_norm, target = clipg_m.group(1).strip(), clipg_m.group(2).strip(), clipg_m.group(3).strip()
            return f"set {target} to ml_gradient_clip_norm({grads}, max_norm={max_norm})"

        # fit gaussian mixture model with <k> components on <data> into <target>
        m_gmm = re.match(
            r"^fit\s+gaussian\s+mixture\s+model\s+with\s+(\d+)\s+components\s+on\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_gmm:
            k, data, target = m_gmm.group(1).strip(), m_gmm.group(2).strip(), m_gmm.group(3).strip()
            return f"set {target} to ml_gmm_fit({data}, k={k})"

        # predict gmm cluster for <samples> using <model> into <target>
        m_gmm_p = re.match(
            r"^predict\s+gmm\s+cluster\s+for\s+(.+?)\s+using\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_gmm_p:
            samples, model, target = m_gmm_p.group(1).strip(), m_gmm_p.group(2).strip(), m_gmm_p.group(3).strip()
            return f"set {target} to ml_gmm_predict({model}, {samples})"

        # compute / calculate pca with <n_components> components on <data> into <target>
        m_pca = re.match(
            r"^(?:calculate|compute)\s+pca\s+with\s+(\d+)\s+components\s+on\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_pca:
            k, data, target = m_pca.group(1).strip(), m_pca.group(2).strip(), m_pca.group(3).strip()
            return f"set {target} to ml_pca_fit({data}, n_components={k})"

        # project data <data> with pca <pca_model> into <target>
        m_pca_proj = re.match(
            r"^project\s+data\s+(.+?)\s+with\s+pca\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_pca_proj:
            data, model, target = m_pca_proj.group(1).strip(), m_pca_proj.group(2).strip(), m_pca_proj.group(3).strip()
            return f"set {target} to ml_pca_transform({model}, {data})"

        # detect anomalies using isolation forest on <data> [trees <n>] [contamination <c>] into <target>
        m_if = re.match(
            r"^detect\s+anomalies\s+using\s+isolation\s+forest\s+on\s+(.+?)(?:\s+trees\s+(\d+))?(?:\s+contamination\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_if:
            data, trees, contam, target = m_if.group(1).strip(), m_if.group(2), m_if.group(3), m_if.group(4).strip()
            t_arg = f", n_trees={trees}" if trees else ""
            c_arg = f", contamination={contam.strip()}" if contam else ""
            return f"set {target} to ml_isolation_forest({data}{t_arg}{c_arg})"

        # cluster data using dbscan on <data> [eps <eps>] [min samples <min_pts>] into <target>
        m_db = re.match(
            r"^cluster\s+data\s+using\s+dbscan\s+on\s+(.+?)(?:\s+eps\s+(.+?))?(?:\s+min\s+samples\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_db:
            data, eps, min_s, target = m_db.group(1).strip(), m_db.group(2), m_db.group(3), m_db.group(4).strip()
            e_arg = f", eps={eps.strip()}" if eps else ""
            m_arg = f", min_samples={min_s}" if min_s else ""
            return f"set {target} to ml_dbscan({data}{e_arg}{m_arg})"

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

            # scale: <c1>, <c2>, ...
            scale_m = re.match(r"^scale(?:_features)?\s*:\s*(.+)$", line, re.IGNORECASE)
            if scale_m:
                raw_feats = scale_m.group(1).split(",")
                spec.scale_features = [f.strip().strip("\"'") for f in raw_feats if f.strip()]
                continue

            # encode: <c1>, <c2>, ...
            encode_m = re.match(r"^encode(?:_features)?\s*:\s*(.+)$", line, re.IGNORECASE)
            if encode_m:
                raw_feats = encode_m.group(1).split(",")
                spec.encode_features = [f.strip().strip("\"'") for f in raw_feats if f.strip()]
                continue

            # algorithm: <algo>
            algo_m = re.match(r"^algorithm\s*:\s*([A-Za-z_]\w*)$", line, re.IGNORECASE)
            if algo_m:
                spec.algorithm = algo_m.group(1).lower()
                continue

            # split: 80% training, 20% testing [with seed <seed>]
            split_m = re.match(
                r"^split\s*:\s*(\d+)%?\s*(?:training|train)?\s*,\s*(\d+)%?\s*(?:testing|test)?(?:\s+with\s+seed\s+(\d+))?",
                line,
                re.IGNORECASE,
            )
            if split_m:
                train_p = float(split_m.group(1)) / 100.0
                test_p = float(split_m.group(2)) / 100.0
                spec.split_train = train_p
                spec.split_test = test_p
                if split_m.group(3):
                    spec.seed = int(split_m.group(3))
                continue

            # seed: <digits>
            seed_m = re.match(r"^seed\s*:\s*(\d+)$", line, re.IGNORECASE)
            if seed_m:
                spec.seed = int(seed_m.group(1))
                continue

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"Model validation error for '{model_name}': {'; '.join(errors)}")

        return spec, model_name
