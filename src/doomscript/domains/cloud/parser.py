"""Independent Domain Parser for Cloud & Object Storage domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.cloud.spec import (
    CloudConnectSpec,
    CloudUploadSpec,
    CloudDownloadSpec,
    CloudListSpec,
    CloudSignedUrlSpec,
)


class CloudDomainParser(DomainParser):
    """Independent parser for Cloud & Object Storage syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # list all files in [bucket] <b_var> [matching <pat>] into <target>
        m_list = re.match(
            r"^list\s+all\s+files\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)(?:\s+matching\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_list:
            b_var = m_list.group(1).strip()
            pat = m_list.group(2).strip() if m_list.group(2) else '""'
            target = m_list.group(3).strip()
            return f"set {target} to list_cloud_files({b_var}, {pat})"

        # generate signed url for <remote> in [bucket] <b_var> [with expiry <sec> seconds] into <target>
        m_url = re.match(
            r"^generate\s+signed\s+url\s+for\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)(?:\s+with\s+expiry\s+(\d+)\s+seconds?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_url:
            remote_expr = m_url.group(1).strip()
            b_var = m_url.group(2).strip()
            expiry = m_url.group(3).strip() if m_url.group(3) else "3600"
            target = m_url.group(4).strip()
            return f"set {target} to generate_cloud_signed_url({b_var}, {remote_expr}, {expiry})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # connect to bucket <name> (as|into) <target>
        m_conn = re.match(
            r"^connect\s+to\s+bucket\s+(.+?)\s+(?:as|into)\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_conn:
            b_name = m_conn.group(1).strip()
            target = m_conn.group(2).strip()
            return f"set {target} to connect_to_bucket({b_name})"

        # upload file <local> to [bucket] <b_var> as <remote>
        m_up = re.match(
            r"^upload\s+file\s+(.+?)\s+to\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+as\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_up:
            local_expr = m_up.group(1).strip()
            b_var = m_up.group(2).strip()
            remote_expr = m_up.group(3).strip()
            return f"upload_cloud_file({b_var}, {local_expr}, {remote_expr})"

        # download file <remote> from [bucket] <b_var> to <local>
        m_down = re.match(
            r"^download\s+file\s+(.+?)\s+from\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+to\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_down:
            remote_expr = m_down.group(1).strip()
            b_var = m_down.group(2).strip()
            local_expr = m_down.group(3).strip()
            return f"download_cloud_file({b_var}, {remote_expr}, {local_expr})"

        # list files in [bucket] <b_var> with prefix <prefix> into <target>
        m_pref = re.match(
            r"^list\s+files\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+with\s+prefix\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pref:
            b_var = m_pref.group(1).strip()
            prefix = m_pref.group(2).strip()
            target = m_pref.group(3).strip()
            return f"set {target} to cloud_list_prefix({b_var}, {prefix})"

        # sync directory <local> to [bucket] <b_var> into <target>
        m_sync = re.match(
            r"^sync\s+directory\s+(.+?)\s+to\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sync:
            local_dir = m_sync.group(1).strip()
            b_var = m_sync.group(2).strip()
            target = m_sync.group(3).strip()
            return f"set {target} to cloud_sync_directory({local_dir}, {b_var})"

        # get metadata of file <file> in [bucket] <b_var> into <target>
        m_meta = re.match(
            r"^get\s+metadata\s+of\s+file\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_meta:
            file_key = m_meta.group(1).strip()
            b_var = m_meta.group(2).strip()
            target = m_meta.group(3).strip()
            return f"set {target} to cloud_file_metadata({b_var}, {file_key})"

        # check if file <file> exists in [bucket] <b_var> into <target>
        m_exists = re.match(
            r"^check\s+if\s+file\s+(.+?)\s+exists\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_exists:
            file_key = m_exists.group(1).strip()
            b_var = m_exists.group(2).strip()
            target = m_exists.group(3).strip()
            return f"set {target} to cloud_file_exists({b_var}, {file_key})"

        # delete files matching <pat> in [bucket] <b_var> into <target>
        m_del = re.match(
            r"^delete\s+files\s+matching\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_del:
            pattern = m_del.group(1).strip()
            b_var = m_del.group(2).strip()
            target = m_del.group(3).strip()
            return f"set {target} to cloud_delete_matching({b_var}, {pattern})"

        # calculate total size of [bucket] <b_var> into <target>
        m_size = re.match(
            r"^calculate\s+total\s+size\s+of\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_size:
            b_var = m_size.group(1).strip()
            target = m_size.group(2).strip()
            return f"set {target} to cloud_bucket_size({b_var})"

        # copy object <src> to <dst> in [bucket] <b_var> into <target>
        m_copy = re.match(
            r"^copy\s+object\s+(.+?)\s+to\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_copy:
            src = m_copy.group(1).strip()
            dst = m_copy.group(2).strip()
            b_var = m_copy.group(3).strip()
            target = m_copy.group(4).strip()
            return f"set {target} to cloud_copy_object({b_var}, {src}, {dst})"

        # generate presigned put url
        m_pput = re.match(
            r"^generate\s+presigned\s+put\s+url\s+for\s+(?:object\s+)?(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)(?:\s+with\s+expiry\s+(\d+)(?:\s+seconds)?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if not m_pput:
            m_pput = re.match(
                r"^generate\s+presigned\s+put\s+url\s+for\s+bucket\s+(.+?)\s+key\s+(.+?)(?:\s+expiry\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
                s,
                re.IGNORECASE,
            )
            if m_pput:
                b_var, key, exp, target = m_pput.group(1).strip(), m_pput.group(2).strip(), m_pput.group(3), m_pput.group(4).strip()
                exp_val = exp.strip() if exp else "3600"
                return f"set {target} to cloud_generate_presigned_put_url({b_var}, {key}, {exp_val})"
        else:
            key, b_var, exp, target = m_pput.group(1).strip(), m_pput.group(2).strip(), m_pput.group(3), m_pput.group(4).strip()
            exp_val = exp.strip() if exp else "3600"
            return f"set {target} to cloud_generate_presigned_put_url({b_var}, {key}, {exp_val})"

        # verify md5 checksum of <key> in [bucket] <b_var> against <hash> into <target>
        m_vmd5 = re.match(
            r"^verify\s+md5\s+checksum\s+of\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+against\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vmd5:
            key, b_var, h_val, target = m_vmd5.group(1).strip(), m_vmd5.group(2).strip(), m_vmd5.group(3).strip(), m_vmd5.group(4).strip()
            return f"set {target} to cloud_verify_md5_checksum({b_var}, {key}, {h_val})"

        # verify sha256 checksum of <key> in [bucket] <b_var> against <hash> into <target>
        m_vsha = re.match(
            r"^verify\s+sha256\s+checksum\s+of\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+against\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vsha:
            key, b_var, h_val, target = m_vsha.group(1).strip(), m_vsha.group(2).strip(), m_vsha.group(3).strip(), m_vsha.group(4).strip()
            return f"set {target} to cloud_verify_sha256_checksum({b_var}, {key}, {h_val})"

        # set object tags for <key> in [bucket] <b_var> to <tags> [into <target>]
        m_stags = re.match(
            r"^set\s+object\s+tags\s+for\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+to\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            s,
            re.IGNORECASE,
        )
        if m_stags:
            key, b_var, tags, target = m_stags.group(1).strip(), m_stags.group(2).strip(), m_stags.group(3).strip(), m_stags.group(4)
            if target:
                return f"set {target.strip()} to cloud_set_object_tags({b_var}, {key}, {tags})"
            return f"cloud_set_object_tags({b_var}, {key}, {tags})"

        # get object tags for <key> in [bucket] <b_var> into <target>
        m_gtags = re.match(
            r"^get\s+object\s+tags\s+for\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gtags:
            key, b_var, target = m_gtags.group(1).strip(), m_gtags.group(2).strip(), m_gtags.group(3).strip()
            return f"set {target} to cloud_get_object_tags({b_var}, {key})"

        # batch delete keys <keys> (from|in) [bucket] <b_var> into <target>
        m_bdel = re.match(
            r"^batch\s+delete\s+keys\s+(.+?)\s+(?:from|in)\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bdel:
            keys, b_var, target = m_bdel.group(1).strip(), m_bdel.group(2).strip(), m_bdel.group(3).strip()
            return f"set {target} to cloud_batch_delete_keys({b_var}, {keys})"

        # filter files in [bucket] <b_var> by size between <min> and <max>
        m_fsize_btwn = re.match(
            r"^filter\s+files\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+by\s+size\s+between\s+(\d+)\s+and\s+(\d+)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fsize_btwn:
            b_var, min_b, max_b, target = m_fsize_btwn.group(1).strip(), m_fsize_btwn.group(2).strip(), m_fsize_btwn.group(3).strip(), m_fsize_btwn.group(4).strip()
            return f"set {target} to cloud_filter_files_by_size({b_var}, {min_b}, {max_b})"

        # filter files in bucket <b_var> by size [min <min_b>] [max <max_b>] into <target>
        m_fsize = re.match(
            r"^filter\s+files\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+by\s+size(?:\s+min\s+(\d+))?(?:\s+max\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fsize:
            b_var, min_b, max_b, target = m_fsize.group(1).strip(), m_fsize.group(2), m_fsize.group(3), m_fsize.group(4).strip()
            min_val = min_b.strip() if min_b else "0"
            max_val = max_b.strip() if max_b else "None"
            return f"set {target} to cloud_filter_files_by_size({b_var}, {min_val}, {max_val})"

        # filter files in [bucket] <b_var> modified after <date> into <target>
        m_fdate = re.match(
            r"^filter\s+files\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+modified\s+after\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fdate:
            b_var, date_val, target = m_fdate.group(1).strip(), m_fdate.group(2).strip(), m_fdate.group(3).strip()
            return f"set {target} to cloud_filter_files_by_date({b_var}, {date_val})"

        # create directory marker <dir> in [bucket] <b_var> into <target>
        m_cdir = re.match(
            r"^create\s+directory\s+marker\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cdir:
            dir_val, b_var, target = m_cdir.group(1).strip(), m_cdir.group(2).strip(), m_cdir.group(3).strip()
            return f"set {target} to cloud_create_directory_marker({b_var}, {dir_val})"

        # move object <src> to <dst> in [bucket] <b_var> [into <target>]
        m_mv = re.match(
            r"^move\s+object\s+(.+?)\s+to\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            s,
            re.IGNORECASE,
        )
        if m_mv:
            src, dst, b_var, target = m_mv.group(1).strip(), m_mv.group(2).strip(), m_mv.group(3).strip(), m_mv.group(4)
            if target:
                return f"set {target.strip()} to cloud_move_object({b_var}, {src}, {dst})"
            return f"cloud_move_object({b_var}, {src}, {dst})"

        # mirror bucket <src> to [bucket] <dst> into <target>
        m_mir = re.match(
            r"^mirror\s+bucket\s+(.+?)\s+to\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mir:
            src, dst, target = m_mir.group(1).strip(), m_mir.group(2).strip(), m_mir.group(3).strip()
            return f"set {target} to cloud_mirror_buckets({src}, {dst})"

        # archive stale files in [bucket] <b_var> older than <days> days [prefix <pfx>] into <target>
        m_arch = re.match(
            r"^archive\s+stale\s+files\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+older\s+than\s+(.+?)\s+days?(?:\s+prefix\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_arch:
            b_var, days, pfx, target = m_arch.group(1).strip(), m_arch.group(2).strip(), m_arch.group(3), m_arch.group(4).strip()
            pfx_val = pfx.strip() if pfx else '"archive/"'
            return f"set {target} to cloud_archive_stale_files({b_var}, {days}, {pfx_val})"

        # export [bucket] manifest for [bucket] <b_var> to <file> into <target>
        m_exp = re.match(
            r"^export\s+(?:bucket\s+)?manifest\s+for\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_exp:
            b_var, file_val, target = m_exp.group(1).strip(), m_exp.group(2).strip(), m_exp.group(3).strip()
            return f"set {target} to cloud_export_bucket_manifest({b_var}, {file_val})"

        # diff bucket[s] <b1> (with|and) [bucket] <b2> into <target>
        m_diff = re.match(
            r"^diff\s+bucket(?:s)?\s+(.+?)\s+(?:with|and)\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_diff:
            b1, b2, target = m_diff.group(1).strip(), m_diff.group(2).strip(), m_diff.group(3).strip()
            return f"set {target} to cloud_diff_buckets({b1}, {b2})"

        # count objects by extension in [bucket] <b_var> into <target>
        m_ext = re.match(
            r"^count\s+objects\s+by\s+extension\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ext:
            b_var, target = m_ext.group(1).strip(), m_ext.group(2).strip()
            return f"set {target} to cloud_count_objects_by_extension({b_var})"

        # read [object] text from object <key> in [bucket] <b_var> into <target>
        m_rtxt2 = re.match(
            r"^read\s+(?:object\s+)?text\s+from\s+object\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rtxt2:
            key, b_var, target = m_rtxt2.group(1).strip(), m_rtxt2.group(2).strip(), m_rtxt2.group(3).strip()
            return f"set {target} to cloud_read_object_text({b_var}, {key})"

        # read object text from bucket <b_var> key <key> into <target>
        m_rtxt = re.match(
            r"^read\s+object\s+text\s+from\s+bucket\s+(.+?)\s+key\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rtxt:
            b_var, key, target = m_rtxt.group(1).strip(), m_rtxt.group(2).strip(), m_rtxt.group(3).strip()
            return f"set {target} to cloud_read_object_text({b_var}, {key})"

        # write [object] text <text> to object <key> in [bucket] <b_var> [into <target>]
        m_wtxt2 = re.match(
            r"^write\s+(?:object\s+)?text\s+(.+?)\s+to\s+object\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            s,
            re.IGNORECASE,
        )
        if m_wtxt2:
            text_val, key, b_var, target = m_wtxt2.group(1).strip(), m_wtxt2.group(2).strip(), m_wtxt2.group(3).strip(), m_wtxt2.group(4)
            if target:
                return f"set {target.strip()} to cloud_write_object_text({b_var}, {key}, {text_val})"
            return f"cloud_write_object_text({b_var}, {key}, {text_val})"

        # write object text <text> to bucket <b_var> key <key> into <target>
        m_wtxt = re.match(
            r"^write\s+object\s+text\s+(.+?)\s+to\s+bucket\s+(.+?)\s+key\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_wtxt:
            text_val, b_var, key, target = m_wtxt.group(1).strip(), m_wtxt.group(2).strip(), m_wtxt.group(3).strip(), m_wtxt.group(4).strip()
            return f"set {target} to cloud_write_object_text({b_var}, {key}, {text_val})"

        # get storage class (of|for) <key> in [bucket] <b_var> into <target>
        m_gcls = re.match(
            r"^get\s+storage\s+class\s+(?:of|for)\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gcls:
            key, b_var, target = m_gcls.group(1).strip(), m_gcls.group(2).strip(), m_gcls.group(3).strip()
            return f"set {target} to cloud_get_storage_class({b_var}, {key})"

        # set storage class (of|for) <key> in [bucket] <b_var> to <cls> [into <target>]
        m_scls = re.match(
            r"^set\s+storage\s+class\s+(?:of|for)\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+to\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            s,
            re.IGNORECASE,
        )
        if m_scls:
            key, b_var, cls_val, target = m_scls.group(1).strip(), m_scls.group(2).strip(), m_scls.group(3).strip(), m_scls.group(4)
            if target:
                return f"set {target.strip()} to cloud_set_storage_class({b_var}, {key}, {cls_val})"
            return f"cloud_set_storage_class({b_var}, {key}, {cls_val})"

        # create rate limiter with capacity <cap> and refill rate <rate> into <target>
        m_rl = re.match(
            r"^create\s+rate\s+limiter\s+with\s+capacity\s+(.+?)\s+and\s+refill\s+rate\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rl:
            cap, rate, target = m_rl.group(1).strip(), m_rl.group(2).strip(), m_rl.group(3).strip()
            return f"set {target} to cloud_rate_limiter_create({cap}, {rate})"

        # acquire <tokens> tokens from rate limiter <limiter> into <target>
        m_acq = re.match(
            r"^acquire\s+(.+?)\s+tokens\s+from\s+rate\s+limiter\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_acq:
            toks, lim, target = m_acq.group(1).strip(), m_acq.group(2).strip(), m_acq.group(3).strip()
            return f"set {target} to cloud_rate_limiter_acquire({lim}, {toks})"

        # create circuit breaker with failure threshold <thresh> into <target>
        m_cb = re.match(
            r"^create\s+circuit\s+breaker\s+with\s+failure\s+threshold\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cb:
            thresh, target = m_cb.group(1).strip(), m_cb.group(2).strip()
            return f"set {target} to cloud_circuit_breaker_create({thresh})"

        # create raft node <node_id> with peers <peers> into <target>
        m_raft = re.match(
            r"^create\s+raft\s+node\s+(.+?)\s+with\s+peers\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_raft:
            nid, peers, target = m_raft.group(1).strip(), m_raft.group(2).strip(), m_raft.group(3).strip()
            return f"set {target} to cloud_raft_create({nid}, {peers})"

        # elect raft leader for <raft> into <target>
        m_elect = re.match(
            r"^elect\s+raft\s+leader\s+for\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_elect:
            raft, target = m_elect.group(1).strip(), m_elect.group(2).strip()
            return f"set {target} to cloud_raft_elect({raft})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Cloud domain does not currently define declarative blocks")
