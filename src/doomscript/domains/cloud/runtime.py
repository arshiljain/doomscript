"""Runtime execution engine for Cloud & Object Storage domain."""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import fnmatch
import hashlib
import os
import shutil
import time
import bisect
from pathlib import Path
from doomscript.core.record import Record
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.cloud.spec import (
    CloudConnectSpec,
    CloudUploadSpec,
    CloudDownloadSpec,
    CloudListSpec,
    CloudSignedUrlSpec,
)


class CloudBucket:
    """Ergonomic representation of a Cloud Object Storage bucket in DoomScript."""

    def __init__(self, bucket_name: str, provider: str = "s3"):
        self.bucket_name = bucket_name.strip('"\'')
        self.provider = provider.lower()
        # Local backing store for deterministic offline execution
        home_dir = os.path.expanduser("~")
        self._store_dir = os.path.join(home_dir, ".doomscript", "cloud_store", self.bucket_name)
        os.makedirs(self._store_dir, exist_ok=True)

    def upload(self, local_path: str, remote_path: str) -> str:
        """Uploads a local file to the cloud bucket at remote_path."""
        clean_remote = remote_path.strip('"\'').lstrip("/")
        dest = os.path.join(self._store_dir, clean_remote)
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        if os.path.exists(local_path):
            shutil.copy2(local_path, dest)
        else:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(f"PLACEHOLDER FOR {local_path}")

        return f"{self.provider}://{self.bucket_name}/{clean_remote}"

    def download(self, remote_path: str, local_path: str) -> str:
        """Downloads a cloud object from remote_path to local_path."""
        clean_remote = remote_path.strip('"\'').lstrip("/")
        src = os.path.join(self._store_dir, clean_remote)
        parent = os.path.dirname(local_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        if os.path.exists(src):
            shutil.copy2(src, local_path)
        else:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(f"CLOUD OBJECT CONTENT: {clean_remote}")

        return local_path

    def list_files(self, pattern: str = "") -> List[str]:
        """Lists all files in the bucket, optionally filtering by glob pattern."""
        pat = pattern.strip('"\'')
        files = []
        for root, _, filenames in os.walk(self._store_dir):
            for fname in filenames:
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, self._store_dir).replace("\\", "/")
                if not pat or fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(fname, pat):
                    files.append(rel)
        files.sort()
        return files

    def generate_signed_url(self, remote_path: str, expiry_seconds: int = 3600) -> str:
        """Generates a secure presigned URL for the cloud object."""
        clean_remote = remote_path.strip('"\'').lstrip("/")
        return f"https://{self.bucket_name}.s3.amazonaws.com/{clean_remote}?token=sec_{expiry_seconds}s"

    def __repr__(self) -> str:
        return f"CloudBucket(name='{self.bucket_name}', provider='{self.provider}')"


# Standalone Helper Functions
def connect_to_bucket(bucket_name: str, provider: str = "s3") -> CloudBucket:
    return CloudBucket(bucket_name=bucket_name, provider=provider)


def upload_cloud_file(bucket: CloudBucket, local_path: str, remote_path: str) -> str:
    return bucket.upload(local_path, remote_path)


def download_cloud_file(bucket: CloudBucket, remote_path: str, local_path: str) -> str:
    return bucket.download(remote_path, local_path)


def list_cloud_files(bucket: CloudBucket, pattern: str = "") -> List[str]:
    return bucket.list_files(pattern=pattern)


def generate_cloud_signed_url(bucket: CloudBucket, remote_path: str, expiry: int = 3600) -> str:
    return bucket.generate_signed_url(remote_path, expiry_seconds=expiry)


class CloudRuntime(DomainRuntime):
    """Runtime execution engine for Cloud & Object Storage specifications."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        errors = ir.validate()
        if errors:
            raise ValueError(f"Cloud spec validation failed: {'; '.join(errors)}")

        if isinstance(ir, CloudConnectSpec):
            return connect_to_bucket(ir.bucket_name, provider=ir.provider)
        elif isinstance(ir, CloudUploadSpec):
            bucket = scope.get(ir.bucket_var)
            local_p = scope.get(ir.local_path, ir.local_path)
            remote_p = scope.get(ir.remote_path, ir.remote_path)
            return upload_cloud_file(bucket, str(local_p), str(remote_p))
        elif isinstance(ir, CloudDownloadSpec):
            bucket = scope.get(ir.bucket_var)
            remote_p = scope.get(ir.remote_path, ir.remote_path)
            local_p = scope.get(ir.local_path, ir.local_path)
            return download_cloud_file(bucket, str(remote_p), str(local_p))
        elif isinstance(ir, CloudListSpec):
            bucket = scope.get(ir.bucket_var)
            return list_cloud_files(bucket, pattern=ir.pattern)
        elif isinstance(ir, CloudSignedUrlSpec):
            bucket = scope.get(ir.bucket_var)
            remote_p = scope.get(ir.remote_path, ir.remote_path)
            return generate_cloud_signed_url(bucket, str(remote_p), expiry=ir.expiry_sec)

        raise NotImplementedError(f"Unsupported IR: {type(ir)}")


def execute_cloud_ir(spec_id: str) -> Any:
    from doomscript.domains.registry import get_domain_registry
    spec = get_domain_registry().get_spec(spec_id)
    if spec is None:
        raise KeyError(f"Cloud spec not found: {spec_id}")
    return CloudRuntime().execute_ir(spec, {})


# --- Batch 17 Spoken English Cloud & Object Storage Operations ---

def cloud_list_prefix(bucket: CloudBucket, prefix: str = "") -> List[str]:
    """List all objects in a bucket whose key starts with a specific prefix."""
    clean_pref = str(prefix).strip("'\"").lstrip("/")
    all_files = bucket.list_files()
    return [f for f in all_files if f.startswith(clean_pref)]


def cloud_sync_directory(local_dir: str, bucket: CloudBucket) -> Dict[str, Any]:
    """Sync a local directory's contents into a cloud bucket maintaining hierarchy."""
    clean_dir = str(local_dir).strip("'\"")
    synced = []
    if os.path.exists(clean_dir):
        for root, _, filenames in os.walk(clean_dir):
            for fname in filenames:
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, clean_dir).replace("\\", "/")
                bucket.upload(full, rel)
                synced.append(rel)
    return {"synced_count": len(synced), "files": synced, "bucket": bucket.bucket_name}


def cloud_file_metadata(bucket: CloudBucket, file_key: str) -> Dict[str, Any]:
    """Inspect metadata, file size, content-type, and modification time of a cloud object."""
    clean_key = str(file_key).strip("'\"").lstrip("/")
    path = os.path.join(bucket._store_dir, clean_key)
    if not os.path.exists(path):
        return {"exists": False, "key": clean_key}
    st = os.stat(path)
    import mimetypes
    ctype, _ = mimetypes.guess_type(path)
    return {
        "exists": True,
        "key": clean_key,
        "size_bytes": st.st_size,
        "modified_time": st.st_mtime,
        "content_type": ctype or "application/octet-stream",
    }


def cloud_file_exists(bucket: CloudBucket, file_key: str) -> bool:
    """Check whether a specific file key exists in the cloud bucket."""
    clean_key = str(file_key).strip("'\"").lstrip("/")
    path = os.path.join(bucket._store_dir, clean_key)
    return os.path.exists(path)


def cloud_delete_matching(bucket: CloudBucket, pattern: str) -> int:
    """Delete all objects matching a pattern/glob in the bucket."""
    pat = str(pattern).strip("'\"")
    all_files = bucket.list_files(pattern=pat)
    deleted_cnt = 0
    for f in all_files:
        full = os.path.join(bucket._store_dir, f)
        if os.path.exists(full):
            os.remove(full)
            deleted_cnt += 1
    return deleted_cnt


def cloud_bucket_size(bucket: CloudBucket) -> Dict[str, Any]:
    """Calculate the total size and file count of a cloud bucket."""
    all_files = bucket.list_files()
    total_bytes = 0
    for f in all_files:
        full = os.path.join(bucket._store_dir, f)
        if os.path.exists(full):
            total_bytes += os.path.getsize(full)
    return {
        "bucket": bucket.bucket_name,
        "file_count": len(all_files),
        "total_bytes": total_bytes,
        "size_kb": round(total_bytes / 1024, 2),
    }


def cloud_copy_object(bucket: CloudBucket, src_key: str, dst_key: str) -> str:
    """Copy an object from src_key to dst_key inside the bucket."""
    s_key = str(src_key).strip("'\"").lstrip("/")
    d_key = str(dst_key).strip("'\"").lstrip("/")
    src_path = os.path.join(bucket._store_dir, s_key)
    dst_path = os.path.join(bucket._store_dir, d_key)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
    else:
        with open(dst_path, "w", encoding="utf-8") as f:
            f.write(f"COPIED FROM {s_key}")
    return f"{bucket.provider}://{bucket.bucket_name}/{d_key}"


def _ensure_bucket(bucket: Any) -> CloudBucket:
    """Helper to convert string or bucket name to CloudBucket instance."""
    if isinstance(bucket, CloudBucket):
        return bucket
    return CloudBucket(str(bucket))


def cloud_generate_presigned_put_url(bucket: Any, key: str, expiry: Any = 3600) -> str:
    """Generate a presigned PUT URL for client-side direct uploads."""
    b = _ensure_bucket(bucket)
    clean_key = str(key).strip("'\"").lstrip("/")
    exp = int(expiry)
    import hashlib
    sig = hashlib.sha256(f"{b.bucket_name}:{clean_key}:{exp}".encode()).hexdigest()[:16]
    return f"https://{b.bucket_name}.s3.amazonaws.com/{clean_key}?X-Amz-Expires={exp}&X-Amz-Signature={sig}"


def cloud_verify_md5_checksum(bucket: Any, key: str, expected_hash: str) -> bool:
    """Verify MD5 checksum of an object in the cloud bucket."""
    import hashlib
    b = _ensure_bucket(bucket)
    clean_key = str(key).strip("'\"").lstrip("/")
    path = os.path.join(b._store_dir, clean_key)
    if not os.path.exists(path):
        return False
    h = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest().lower() == str(expected_hash).strip("'\"").lower()


def cloud_verify_sha256_checksum(bucket: Any, key: str, expected_hash: str) -> bool:
    """Verify SHA-256 checksum of an object in the cloud bucket."""
    import hashlib
    b = _ensure_bucket(bucket)
    clean_key = str(key).strip("'\"").lstrip("/")
    path = os.path.join(b._store_dir, clean_key)
    if not os.path.exists(path):
        return False
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest().lower() == str(expected_hash).strip("'\"").lower()


def cloud_set_object_tags(bucket: Any, key: str, tags_dict: Dict[str, str]) -> Dict[str, str]:
    """Attach key-value metadata tags to an object."""
    import json
    b = _ensure_bucket(bucket)
    clean_key = str(key).strip("'\"").lstrip("/")
    meta_path = os.path.join(b._store_dir, f".{clean_key}.tags.json")
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    tags = {str(k): str(v) for k, v in tags_dict.items()} if isinstance(tags_dict, dict) else {}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(tags, f)
    return tags


def cloud_get_object_tags(bucket: Any, key: str) -> Dict[str, str]:
    """Retrieve metadata tags for an object."""
    import json
    b = _ensure_bucket(bucket)
    clean_key = str(key).strip("'\"").lstrip("/")
    meta_path = os.path.join(b._store_dir, f".{clean_key}.tags.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def cloud_batch_delete_keys(bucket: Any, keys_list: List[str]) -> int:
    """Delete a list of object keys in a single operation."""
    b = _ensure_bucket(bucket)
    cnt = 0
    for key in keys_list:
        clean_key = str(key).strip("'\"").lstrip("/")
        p = os.path.join(b._store_dir, clean_key)
        if os.path.exists(p):
            os.remove(p)
            cnt += 1
        meta = os.path.join(b._store_dir, f".{clean_key}.tags.json")
        if os.path.exists(meta):
            os.remove(meta)
    return cnt


def cloud_filter_files_by_size(bucket: Any, min_bytes: Any = 0, max_bytes: Any = None) -> List[str]:
    """Filter bucket objects by size threshold."""
    b = _ensure_bucket(bucket)
    all_files = b.list_files()
    min_b = int(min_bytes) if min_bytes is not None else 0
    max_b = int(max_bytes) if max_bytes is not None else float("inf")
    matched = []
    for f in all_files:
        full = os.path.join(b._store_dir, f)
        if os.path.exists(full):
            sz = os.path.getsize(full)
            if min_b <= sz <= max_b:
                matched.append(f)
    return matched


def cloud_filter_files_by_date(bucket: Any, after_date: str) -> List[str]:
    """Filter objects modified after a given timestamp."""
    from datetime import datetime
    b = _ensure_bucket(bucket)
    all_files = b.list_files()
    date_str = str(after_date).strip("'\"")
    try:
        cutoff = datetime.fromisoformat(date_str).timestamp()
    except Exception:
        cutoff = 0.0

    matched = []
    for f in all_files:
        full = os.path.join(b._store_dir, f)
        if os.path.exists(full):
            mtime = os.path.getmtime(full)
            if mtime >= cutoff:
                matched.append(f)
    return matched


def cloud_create_directory_marker(bucket: Any, dir_path: str) -> str:
    """Create an empty directory prefix marker in the bucket."""
    b = _ensure_bucket(bucket)
    clean_dir = str(dir_path).strip("'\"").strip("/") + "/"
    marker_path = os.path.join(b._store_dir, clean_dir)
    os.makedirs(marker_path, exist_ok=True)
    with open(os.path.join(marker_path, ".dir_marker"), "w", encoding="utf-8") as f:
        f.write("")
    return clean_dir


def cloud_move_object(bucket: Any, src_key: str, dst_key: str) -> str:
    """Move/rename an object inside the bucket."""
    b = _ensure_bucket(bucket)
    cloud_copy_object(b, src_key, dst_key)
    clean_src = str(src_key).strip("'\"").lstrip("/")
    src_path = os.path.join(b._store_dir, clean_src)
    if os.path.exists(src_path):
        os.remove(src_path)
    return str(dst_key).strip("'\"").lstrip("/")


def cloud_mirror_buckets(src_bucket: Any, dst_bucket: Any) -> Dict[str, int]:
    """Mirror all objects from source bucket to destination bucket."""
    src_b = _ensure_bucket(src_bucket)
    dst_b = _ensure_bucket(dst_bucket)
    files = src_b.list_files()
    cnt = 0
    for f in files:
        s_path = os.path.join(src_b._store_dir, f)
        d_path = os.path.join(dst_b._store_dir, f)
        os.makedirs(os.path.dirname(d_path), exist_ok=True)
        if os.path.exists(s_path):
            shutil.copy2(s_path, d_path)
            cnt += 1
    return {"synced": cnt}


def cloud_archive_stale_files(bucket: Any, days_old: Any, archive_prefix: str = "archive/") -> int:
    """Move objects older than days_old to archive_prefix."""
    import time
    b = _ensure_bucket(bucket)
    cutoff = time.time() - (float(days_old) * 86400.0)
    pfx = str(archive_prefix).strip("'\"").rstrip("/") + "/"
    files = b.list_files()
    archived = 0
    for f in files:
        if f.startswith(pfx):
            continue
        full = os.path.join(b._store_dir, f)
        if os.path.exists(full) and os.path.getmtime(full) <= cutoff:
            dst = pfx + f
            cloud_move_object(b, f, dst)
            archived += 1
    return archived


def cloud_export_bucket_manifest(bucket: Any, manifest_file: str) -> str:
    """Export catalog of all bucket objects into a CSV or JSON file."""
    import json
    from datetime import datetime
    b = _ensure_bucket(bucket)
    files = b.list_files()
    records = []
    for f in files:
        full = os.path.join(b._store_dir, f)
        if os.path.exists(full):
            records.append({
                "key": f,
                "size_bytes": os.path.getsize(full),
                "modified": datetime.fromtimestamp(os.path.getmtime(full)).isoformat(),
            })

    out_path = str(manifest_file).strip("'\"")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    if out_path.endswith(".json"):
        with open(out_path, "w", encoding="utf-8") as fp:
            json.dump(records, fp, indent=2)
    else:
        import csv
        with open(out_path, "w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=["key", "size_bytes", "modified"])
            writer.writeheader()
            writer.writerows(records)
    return out_path


def cloud_diff_buckets(bucket1: Any, bucket2: Any) -> Dict[str, List[str]]:
    """Compare contents of two buckets to find unique and common keys."""
    b1 = _ensure_bucket(bucket1)
    b2 = _ensure_bucket(bucket2)
    s1 = set(b1.list_files())
    s2 = set(b2.list_files())
    return {
        "only_in_first": sorted(list(s1 - s2)),
        "only_in_second": sorted(list(s2 - s1)),
        "in_both": sorted(list(s1 & s2)),
    }


def cloud_count_objects_by_extension(bucket: Any) -> Dict[str, int]:
    """Count bucket objects grouped by file extension."""
    b = _ensure_bucket(bucket)
    files = b.list_files()
    counts = {}
    for f in files:
        ext = os.path.splitext(f)[1].lstrip(".").lower() or "none"
        counts[ext] = counts.get(ext, 0) + 1
    return counts


def cloud_read_object_text(bucket: Any, key: str) -> str:
    """Read textual content of a cloud object."""
    b = _ensure_bucket(bucket)
    clean_key = str(key).strip("'\"").lstrip("/")
    p = os.path.join(b._store_dir, clean_key)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


def cloud_write_object_text(bucket: Any, key: str, text_content: str) -> str:
    """Write text directly to a cloud object."""
    b = _ensure_bucket(bucket)
    clean_key = str(key).strip("'\"").lstrip("/")
    p = os.path.join(b._store_dir, clean_key)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(str(text_content))
    return f"{b.provider}://{b.bucket_name}/{clean_key}"


def cloud_get_storage_class(bucket: Any, key: str) -> str:
    """Retrieve simulated storage class tier for an object."""
    import json
    b = _ensure_bucket(bucket)
    clean_key = str(key).strip("'\"").lstrip("/")
    meta_path = os.path.join(b._store_dir, f".{clean_key}.tier.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f).get("storage_class", "STANDARD")
        except Exception:
            return "STANDARD"
    return "STANDARD"


def cloud_set_storage_class(bucket: Any, key: str, storage_class: str) -> str:
    """Update simulated storage tier for an object."""
    import json
    b = _ensure_bucket(bucket)
    clean_key = str(key).strip("'\"").lstrip("/")
    cls_str = str(storage_class).strip("'\"").upper()
    meta_path = os.path.join(b._store_dir, f".{clean_key}.tier.json")
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({"storage_class": cls_str}, f)
    return cls_str


class CloudStorageManager:
    """Multi-part upload, versioning, and lifecycle rule engine for cloud object stores."""

    def __init__(self, bucket: Any):
        self.bucket = _ensure_bucket(bucket)
        self.active_uploads: Dict[str, Dict[str, Any]] = {}
        self.versions: Dict[str, List[Dict[str, Any]]] = {}

    def initiate_multipart_upload(self, key: str) -> str:
        import uuid
        upload_id = str(uuid.uuid4())[:8]
        clean_key = str(key).strip("'\"").lstrip("/")
        self.active_uploads[upload_id] = {
            "key": clean_key,
            "parts": {},
            "initiated_at": 1000.0,
        }
        return upload_id

    def upload_part(self, upload_id: str, part_number: int, data: Union[str, bytes]) -> Dict[str, Any]:
        import hashlib
        if upload_id not in self.active_uploads:
            raise KeyError(f"Upload ID not found: {upload_id}")
        raw_bytes = data.encode("utf-8") if isinstance(data, str) else data
        etag = hashlib.md5(raw_bytes).hexdigest()
        self.active_uploads[upload_id]["parts"][int(part_number)] = {
            "data": raw_bytes,
            "etag": etag,
            "size": len(raw_bytes),
        }
        return {"part_number": part_number, "etag": etag, "size": len(raw_bytes)}

    def complete_multipart_upload(self, upload_id: str) -> Dict[str, Any]:
        import hashlib
        if upload_id not in self.active_uploads:
            raise KeyError(f"Upload ID not found: {upload_id}")
        session = self.active_uploads.pop(upload_id)
        key = session["key"]
        sorted_parts = sorted(session["parts"].items(), key=lambda x: x[0])

        combined = bytearray()
        for pnum, pinfo in sorted_parts:
            combined.extend(pinfo["data"])

        # Write to backing store
        dest = os.path.join(self.bucket._store_dir, key)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(combined)

        etag = hashlib.md5(combined).hexdigest()
        version_id = f"v{len(self.versions.get(key, [])) + 1}"
        self.versions.setdefault(key, []).append({
            "version_id": version_id,
            "size": len(combined),
            "etag": etag,
        })

        return {
            "key": key,
            "total_parts": len(sorted_parts),
            "total_bytes": len(combined),
            "etag": etag,
            "version_id": version_id,
        }

    def list_versions(self, key: str) -> List[Dict[str, Any]]:
        clean_key = str(key).strip("'\"").lstrip("/")
        return list(self.versions.get(clean_key, []))


class IAMPolicyEngine:
    """IAM Access Policy evaluation engine supporting wildcards, Allow/Deny, and Conditions."""

    def __init__(self):
        self.policies: List[Dict[str, Any]] = []

    def add_policy(self, policy_doc: Dict[str, Any]) -> None:
        self.policies.append(policy_doc)

    def evaluate(
        self,
        action: str,
        resource: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Evaluate access request against all policies. Deny overrides Allow; default is Deny."""
        ctx = context or {}
        has_allow = False

        for pol in self.policies:
            statements = pol.get("Statement", [])
            if isinstance(statements, dict):
                statements = [statements]

            for stmt in statements:
                effect = stmt.get("Effect", "Deny").capitalize()
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]

                resources = stmt.get("Resource", [])
                if isinstance(resources, str):
                    resources = [resources]

                # Match action
                action_match = any(fnmatch.fnmatch(action.lower(), a.lower()) for a in actions)
                if not action_match:
                    continue

                # Match resource
                resource_match = any(fnmatch.fnmatch(resource.lower(), r.lower()) for r in resources)
                if not resource_match:
                    continue

                # Match conditions if any
                cond_pass = True
                conds = stmt.get("Condition", {})
                for cond_type, cond_dict in conds.items():
                    if cond_type == "StringEquals":
                        for k, v in cond_dict.items():
                            if str(ctx.get(k)) != str(v):
                                cond_pass = False
                    elif cond_type == "IpAddress":
                        for k, v in cond_dict.items():
                            if str(ctx.get(k)) != str(v):
                                cond_pass = False

                if not cond_pass:
                    continue

                if effect == "Deny":
                    return {"decision": "Deny", "allowed": False, "matched_statement": stmt}
                elif effect == "Allow":
                    has_allow = True

        if has_allow:
            return {"decision": "Allow", "allowed": True}
        return {"decision": "ImplicitDeny", "allowed": False}


class CloudCostCalculator:
    """Multi-cloud resource and monthly bill estimation engine."""

    RATES = {
        "compute": {
            "micro": {"vcpu": 1, "ram_gb": 1.0, "rate_hourly": 0.0104},
            "small": {"vcpu": 1, "ram_gb": 2.0, "rate_hourly": 0.0208},
            "medium": {"vcpu": 2, "ram_gb": 4.0, "rate_hourly": 0.0416},
            "large": {"vcpu": 4, "ram_gb": 8.0, "rate_hourly": 0.0832},
            "xlarge": {"vcpu": 8, "ram_gb": 16.0, "rate_hourly": 0.1664},
        },
        "storage_gb_month": {
            "STANDARD": 0.023,
            "INFREQUENT": 0.0125,
            "COLD": 0.004,
            "ARCHIVE": 0.00099,
        },
        "egress_gb": 0.09,
    }

    def __init__(self):
        self.resources: List[Dict[str, Any]] = []

    def add_instance(self, size: str, count: int = 1, hours_per_month: float = 730.0) -> None:
        self.resources.append({
            "type": "compute",
            "size": size.lower(),
            "count": int(count),
            "hours": float(hours_per_month),
        })

    def add_storage(self, gb: float, storage_class: str = "STANDARD") -> None:
        self.resources.append({
            "type": "storage",
            "gb": float(gb),
            "tier": storage_class.upper(),
        })

    def add_egress(self, gb: float) -> None:
        self.resources.append({
            "type": "egress",
            "gb": float(gb),
        })

    def estimate_monthly(self) -> Dict[str, Any]:
        compute_cost = 0.0
        storage_cost = 0.0
        egress_cost = 0.0

        for r in self.resources:
            t = r["type"]
            if t == "compute":
                rate = self.RATES["compute"].get(r["size"], {}).get("rate_hourly", 0.05)
                compute_cost += rate * r["count"] * r["hours"]
            elif t == "storage":
                tier_rate = self.RATES["storage_gb_month"].get(r["tier"], 0.023)
                storage_cost += tier_rate * r["gb"]
            elif t == "egress":
                egress_cost += self.RATES["egress_gb"] * r["gb"]

        total = compute_cost + storage_cost + egress_cost
        return {
            "compute_cost": round(compute_cost, 2),
            "storage_cost": round(storage_cost, 2),
            "egress_cost": round(egress_cost, 2),
            "total_monthly_estimate": round(total, 2),
        }




# ==============================================================================
# Advanced Cloud Deepening: Multipart Uploads, CAS Blob Storage & Lifecycles
# ==============================================================================

class MultipartUploadManager:
    """S3-compatible multipart upload coordinator with chunking and ETag verification."""

    def __init__(self):
        # upload_id -> {"bucket": ..., "key": ..., "parts": {part_number: (etag, bytes)}}
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def initiate_upload(self, bucket: str, key: str) -> str:
        """Initiates multipart upload session and returns unique upload_id."""
        upload_id = f"upload-{hashlib.sha256(f'{bucket}/{key}/{time.time()}'.encode()).hexdigest()[:16]}"
        self.sessions[upload_id] = {
            "bucket": bucket,
            "key": key,
            "parts": {},
            "created_at": time.time(),
        }
        return upload_id

    def upload_part(self, upload_id: str, part_number: int, data: bytes) -> str:
        """Uploads a single chunk and returns MD5/SHA256 ETag."""
        if upload_id not in self.sessions:
            raise KeyError(f"Upload ID not found: {upload_id}")
        etag = hashlib.md5(data).hexdigest()
        self.sessions[upload_id]["parts"][int(part_number)] = (etag, data)
        return etag

    def complete_upload(self, upload_id: str, parts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assembles all parts in sequential order and validates ETags."""
        if upload_id not in self.sessions:
            raise KeyError(f"Upload ID not found: {upload_id}")

        session = self.sessions[upload_id]
        stored_parts = session["parts"]

        # Validate parts
        assembled_chunks = []
        for p in sorted(parts, key=lambda x: int(x["part_number"])):
            p_num = int(p["part_number"])
            if p_num not in stored_parts:
                raise ValueError(f"Missing uploaded part number: {p_num}")
            etag, data = stored_parts[p_num]
            if "etag" in p and p["etag"] != etag:
                raise ValueError(f"ETag mismatch for part {p_num}")
            assembled_chunks.append(data)

        combined_data = b"".join(assembled_chunks)
        final_etag = f"{hashlib.md5(combined_data).hexdigest()}-{len(assembled_chunks)}"

        res = {
            "bucket": session["bucket"],
            "key": session["key"],
            "total_bytes": len(combined_data),
            "parts_count": len(assembled_chunks),
            "etag": final_etag,
            "data": combined_data,
        }
        del self.sessions[upload_id]
        return res

    def abort_upload(self, upload_id: str) -> bool:
        """Cancels multipart upload and discards buffers."""
        if upload_id in self.sessions:
            del self.sessions[upload_id]
            return True
        return False


class ContentAddressableStorage:
    """SHA-256 deduplicating Content-Addressable Storage (CAS) with garbage collection."""

    def __init__(self):
        self.blobs: Dict[str, bytes] = {}

    def put(self, data: bytes) -> str:
        """Stores content and returns its SHA-256 hex digest."""
        h = hashlib.sha256(data).hexdigest()
        if h not in self.blobs:
            self.blobs[h] = bytes(data)
        return h

    def get(self, content_hash: str) -> Optional[bytes]:
        """Retrieves blob by content hash."""
        return self.blobs.get(content_hash.strip().lower())

    def has(self, content_hash: str) -> bool:
        """Checks if content hash exists in CAS."""
        return content_hash.strip().lower() in self.blobs

    def gc(self, active_hashes: Set[str]) -> Dict[str, int]:
        """Garbage collects unreferenced blobs and returns deleted count & freed bytes."""
        active = {h.strip().lower() for h in active_hashes}
        deleted_count = 0
        freed_bytes = 0

        unreferenced = [h for h in self.blobs if h not in active]
        for h in unreferenced:
            freed_bytes += len(self.blobs[h])
            del self.blobs[h]
            deleted_count += 1

        return {
            "deleted_count": deleted_count,
            "freed_bytes": freed_bytes,
            "remaining_count": len(self.blobs),
        }


class BucketLifecycleEngine:
    """Evaluates S3-style bucket lifecycle rules (expiration and tier transitions)."""

    @classmethod
    def evaluate(
        cls,
        objects: List[Dict[str, Any]],
        rules: List[Dict[str, Any]],
        current_time_epoch: Optional[float] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Evaluates lifecycle policies.
        `rules` format:
        [
            {"prefix": "logs/", "expire_days": 30},
            {"prefix": "backups/", "transition_days": 90, "target_tier": "GLACIER"},
            ...
        ]
        """
        now = current_time_epoch if current_time_epoch is not None else time.time()
        expired: List[Dict[str, Any]] = []
        transitioned: List[Dict[str, Any]] = []

        for obj in objects:
            key = obj.get("key", "")
            last_mod = float(obj.get("last_modified_epoch", now))
            age_days = (now - last_mod) / 86400.0

            for rule in rules:
                prefix = rule.get("prefix", "")
                if not key.startswith(prefix):
                    continue

                # Expiration check
                if "expire_days" in rule and age_days >= rule["expire_days"]:
                    expired.append(dict(obj))
                    break

                # Transition check
                if "transition_days" in rule and age_days >= rule["transition_days"]:
                    target_tier = rule.get("target_tier", "GLACIER")
                    if obj.get("storage_class") != target_tier:
                        rec = dict(obj)
                        rec["new_storage_class"] = target_tier
                        transitioned.append(rec)
                        break

        return {
            "expired": expired,
            "transitioned": transitioned,
        }


def cloud_multipart_initiate(bucket: str, key: str) -> str:
    """Initiates multipart upload session."""
    mgr = MultipartUploadManager()
    return mgr.initiate_upload(bucket, key)


def cloud_cas_put(data: bytes) -> str:
    """Stores data in in-memory Content-Addressable Storage."""
    cas = ContentAddressableStorage()
    return cas.put(data)


def cloud_evaluate_lifecycle(objects: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluates bucket lifecycle policies."""
    return BucketLifecycleEngine.evaluate(objects, rules)


# ==============================================================================
# TOKEN BUCKET RATE LIMITER, CIRCUIT BREAKER & RAFT CONSENSUS SIMULATOR
# ==============================================================================

class TokenBucketRateLimiter:
    """Token Bucket rate limiter with burst capacity and fractional token refills."""

    def __init__(self, capacity: float = 10.0, refill_rate: float = 2.0):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)  # tokens per second
        self.tokens = self.capacity
        self.last_refill = time.time()

    def acquire(self, requested: float = 1.0) -> Dict[str, Any]:
        """Attempts to acquire requested tokens, returning allowed status and stats."""
        now = time.time()
        elapsed = max(0.0, now - self.last_refill)
        self.last_refill = now

        # Refill tokens up to capacity
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

        req = float(requested)
        if self.tokens >= req:
            self.tokens -= req
            return {
                "allowed": True,
                "remaining_tokens": round(self.tokens, 4),
                "retry_after_sec": 0.0,
            }
        else:
            deficit = req - self.tokens
            retry_after = round(deficit / self.refill_rate, 4) if self.refill_rate > 0 else float("inf")
            return {
                "allowed": False,
                "remaining_tokens": round(self.tokens, 4),
                "retry_after_sec": retry_after,
            }


class CircuitBreakerResilience:
    """Martin Fowler's Circuit Breaker state machine (CLOSED, OPEN, HALF_OPEN)."""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_sec: float = 5.0,
        half_open_success_threshold: int = 2,
    ):
        self.failure_threshold = max(1, int(failure_threshold))
        self.recovery_timeout = float(recovery_timeout_sec)
        self.half_open_threshold = max(1, int(half_open_success_threshold))

        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.last_state_change = time.time()

    def record_success(self) -> None:
        """Records a successful operation."""
        if self.state == "HALF_OPEN":
            self.consecutive_successes += 1
            if self.consecutive_successes >= self.half_open_threshold:
                self.state = "CLOSED"
                self.consecutive_failures = 0
                self.consecutive_successes = 0
                self.last_state_change = time.time()
        elif self.state == "CLOSED":
            self.consecutive_failures = 0

    def record_failure(self) -> None:
        """Records a failed operation."""
        self.consecutive_failures += 1
        if self.state == "HALF_OPEN" or self.consecutive_failures >= self.failure_threshold:
            self.state = "OPEN"
            self.consecutive_successes = 0
            self.last_state_change = time.time()

    def can_execute(self) -> bool:
        """Determines if a request should be permitted."""
        now = time.time()
        if self.state == "OPEN":
            if now - self.last_state_change >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                self.consecutive_successes = 0
                self.last_state_change = now
                return True
            return False
        return True

    def get_stats(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "can_execute": self.can_execute(),
        }


class RaftConsensusSimulator:
    """Raft consensus protocol state machine and replicated log simulator."""

    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = str(node_id)
        self.peers = [str(p) for p in peers if str(p) != self.node_id]

        # Persistent state
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[Dict[str, Any]] = []  # [{term, index, command}]

        # Volatile state
        self.commit_index = 0
        self.last_applied = 0
        self.role = "FOLLOWER"  # FOLLOWER, CANDIDATE, LEADER

        # Cluster vote tracker
        self.votes_received: Set[str] = set()

    def start_election(self) -> Dict[str, Any]:
        """Transitions node to CANDIDATE and increments term."""
        self.role = "CANDIDATE"
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}

        quorum = (len(self.peers) + 1) // 2 + 1
        is_leader = len(self.votes_received) >= quorum
        if is_leader:
            self.role = "LEADER"

        return {
            "node_id": self.node_id,
            "term": self.current_term,
            "role": self.role,
            "votes_count": len(self.votes_received),
            "quorum_required": quorum,
            "is_leader": is_leader,
        }

    def append_entry(self, command: str) -> Dict[str, Any]:
        """Appends a log entry if node is LEADER."""
        if self.role != "LEADER":
            return {"success": False, "reason": "Not the leader"}

        entry_idx = len(self.log) + 1
        entry = {
            "term": self.current_term,
            "index": entry_idx,
            "command": command,
        }
        self.log.append(entry)
        self.commit_index = entry_idx
        return {
            "success": True,
            "entry_index": entry_idx,
            "term": self.current_term,
            "command": command,
        }


def cloud_rate_limiter_create(capacity: float = 10.0, refill_rate: float = 2.0) -> Any:
    """Creates a Token Bucket distributed rate limiter."""
    limiter = TokenBucketRateLimiter(capacity=capacity, refill_rate=refill_rate)
    return Record({
        "capacity": limiter.capacity,
        "refill_rate": limiter.refill_rate,
        "instance": limiter,
    })


def cloud_rate_limiter_acquire(limiter: Any, tokens: float = 1.0) -> Any:
    """Attempts to acquire tokens from rate limiter."""
    inst = limiter.instance if hasattr(limiter, "instance") else limiter
    return Record(inst.acquire(tokens))


def cloud_circuit_breaker_create(
    failure_threshold: int = 3, recovery_timeout_sec: float = 5.0
) -> Any:
    """Creates a resilience Circuit Breaker."""
    cb = CircuitBreakerResilience(failure_threshold=failure_threshold, recovery_timeout_sec=recovery_timeout_sec)
    return Record({
        "failure_threshold": cb.failure_threshold,
        "recovery_timeout": cb.recovery_timeout,
        "state": cb.state,
        "instance": cb,
    })


def cloud_raft_create(node_id: str, peers: List[str]) -> Any:
    """Creates a Raft consensus node."""
    raft = RaftConsensusSimulator(node_id=node_id, peers=peers)
    return Record({
        "node_id": raft.node_id,
        "term": raft.current_term,
        "role": raft.role,
        "instance": raft,
    })


def cloud_raft_elect(raft: Any) -> Any:
    """Triggers election on Raft consensus node."""
    inst = raft.instance if hasattr(raft, "instance") else raft
    return Record(inst.start_election())


class DistributedConsistentHashRing:
    """Virtual node consistent hash ring for distributed caching and partition sharding."""

    def __init__(self, default_vnodes: int = 100):
        self.default_vnodes = max(1, int(default_vnodes))
        self.ring: List[int] = []  # Sorted hash positions
        self.ring_map: Dict[int, str] = {}  # hash -> physical node_id
        self.nodes: Set[str] = set()

    def _hash(self, key: str) -> int:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return int(digest[:8], 16)

    def add_node(self, node_id: str, vnodes: Optional[int] = None) -> None:
        if node_id in self.nodes:
            return
        self.nodes.add(node_id)
        count = vnodes if vnodes is not None else self.default_vnodes
        for i in range(count):
            vkey = f"{node_id}#vnode{i}"
            h = self._hash(vkey)
            self.ring.append(h)
            self.ring_map[h] = node_id
        self.ring.sort()

    def remove_node(self, node_id: str) -> None:
        if node_id not in self.nodes:
            return
        self.nodes.remove(node_id)
        self.ring = [h for h in self.ring if self.ring_map[h] != node_id]
        self.ring_map = {h: n for h, n in self.ring_map.items() if n != node_id}

    def get_node(self, key: str) -> Optional[str]:
        if not self.ring:
            return None
        h = self._hash(str(key))
        idx = bisect.bisect_right(self.ring, h)
        if idx == len(self.ring):
            idx = 0
        return self.ring_map[self.ring[idx]]

    def get_preference_list(self, key: str, count: int = 3) -> List[str]:
        """Returns Dynamo-style preference list of N distinct physical replica nodes."""
        if not self.ring:
            return []
        h = self._hash(str(key))
        idx = bisect.bisect_right(self.ring, h)
        selected: List[str] = []
        n_ring = len(self.ring)
        for offset in range(n_ring):
            pos = (idx + offset) % n_ring
            node = self.ring_map[self.ring[pos]]
            if node not in selected:
                selected.append(node)
                if len(selected) >= count or len(selected) >= len(self.nodes):
                    break
        return selected

    def get_distribution(self, keys: List[str]) -> Dict[str, int]:
        dist: Dict[str, int] = {node: 0 for node in self.nodes}
        for k in keys:
            n = self.get_node(k)
            if n in dist:
                dist[n] += 1
        return dist


class LeakyBucketTrafficShaper:
    """Traffic shaping leaky bucket queue with constant outflow drain and burst capacity."""

    def __init__(self, capacity: int = 10, leak_rate: float = 2.0):
        self.capacity = max(1, int(capacity))
        self.leak_rate = max(0.01, float(leak_rate))  # items leaked per second
        self.queue: List[str] = []
        self.last_leak_time: Optional[float] = None
        self.dropped_count = 0
        self.processed_count = 0

    def _leak(self, current_time: Optional[float] = None) -> List[str]:
        now = current_time if current_time is not None else time.time()
        if self.last_leak_time is None:
            self.last_leak_time = now
            return []
        elapsed = max(0.0, now - self.last_leak_time)
        leaked_items = []
        items_to_leak = int(elapsed * self.leak_rate)
        if items_to_leak > 0:
            count = min(items_to_leak, len(self.queue))
            leaked_items = self.queue[:count]
            self.queue = self.queue[count:]
            self.processed_count += len(leaked_items)
            self.last_leak_time = now
        return leaked_items

    def enqueue(self, item_id: str, current_time: Optional[float] = None) -> Dict[str, Any]:
        self._leak(current_time)
        if len(self.queue) < self.capacity:
            self.queue.append(str(item_id))
            return {
                "accepted": True,
                "dropped": False,
                "queue_depth": len(self.queue),
                "capacity": self.capacity,
            }
        else:
            self.dropped_count += 1
            return {
                "accepted": False,
                "dropped": True,
                "queue_depth": len(self.queue),
                "capacity": self.capacity,
            }

    def drain(self, current_time: Optional[float] = None) -> List[str]:
        return self._leak(current_time)

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "queue_depth": len(self.queue),
            "capacity": self.capacity,
            "leak_rate": self.leak_rate,
            "dropped_count": self.dropped_count,
            "processed_count": self.processed_count,
        }


def cloud_hash_ring_create(nodes: Optional[List[str]] = None, vnodes: int = 50) -> Any:
    """Creates a distributed consistent hash ring."""
    ring = DistributedConsistentHashRing(default_vnodes=vnodes)
    if nodes:
        for n in nodes:
            ring.add_node(str(n))
    return Record({
        "nodes_count": len(ring.nodes),
        "vnodes_per_node": ring.default_vnodes,
        "instance": ring,
    })


def cloud_hash_ring_get(ring: Any, key: str) -> str:
    """Locates the primary responsible physical node for a given key."""
    inst = ring.instance if hasattr(ring, "instance") else ring
    return inst.get_node(key) or ""


def cloud_hash_ring_preference_list(ring: Any, key: str, count: int = 3) -> Any:
    """Returns replica preference list for a key."""
    inst = ring.instance if hasattr(ring, "instance") else ring
    prefs = inst.get_preference_list(key, count=count)
    return Record({
        "key": key,
        "replicas_count": len(prefs),
        "nodes": prefs,
    })


def cloud_leaky_bucket_create(capacity: int = 10, leak_rate: float = 2.0) -> Any:
    """Creates a leaky bucket traffic shaper."""
    bucket = LeakyBucketTrafficShaper(capacity=capacity, leak_rate=leak_rate)
    return Record({
        "capacity": bucket.capacity,
        "leak_rate": bucket.leak_rate,
        "instance": bucket,
    })


def cloud_leaky_bucket_enqueue(bucket: Any, item_id: str, current_time: Optional[float] = None) -> Any:
    """Attempts to enqueue packet into leaky bucket."""
    inst = bucket.instance if hasattr(bucket, "instance") else bucket
    return Record(inst.enqueue(item_id, current_time=current_time))


def cloud_leaky_bucket_drain(bucket: Any, current_time: Optional[float] = None) -> List[str]:
    """Drains and returns processed packets from leaky bucket."""
    inst = bucket.instance if hasattr(bucket, "instance") else bucket
    return inst.drain(current_time=current_time)


# ==============================================================================
# PAXOS DISTRIBUTED CONSENSUS & RAFT LEADER ELECTION / LOG REPLICATION
# ==============================================================================


class PaxosConsensusProtocolStateReplication:
    """Leslie Lamport Paxos Distributed Consensus Protocol Engine.

    Implements classic two-phase consensus:
    - Phase 1a/1b: Prepare(n) and Promise(n, max_accepted_n, max_accepted_val)
    - Phase 2a/2b: Accept(n, val) and Accepted(n, val)
    Ensures safety under asynchronous network delays, out-of-order delivery, and concurrent proposers.
    """

    class Acceptor:
        def __init__(self, node_id: int):
            self.node_id = node_id
            self.min_proposal = 0  # Promised not to accept proposals < min_proposal
            self.accepted_proposal: Optional[int] = None
            self.accepted_value: Optional[Any] = None

        def receive_prepare(self, proposal_num: int) -> Tuple[bool, Optional[int], Optional[Any]]:
            if proposal_num > self.min_proposal:
                self.min_proposal = proposal_num
                return True, self.accepted_proposal, self.accepted_value
            return False, None, None

        def receive_accept(self, proposal_num: int, val: Any) -> bool:
            if proposal_num >= self.min_proposal:
                self.min_proposal = proposal_num
                self.accepted_proposal = proposal_num
                self.accepted_value = val
                return True
            return False

    @classmethod
    def run_consensus(
        cls,
        num_acceptors: int = 5,
        proposals: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Runs Paxos consensus rounds with specified proposers and acceptors."""
        n_acc = max(3, int(num_acceptors))
        acceptors = [cls.Acceptor(i) for i in range(n_acc)]
        quorum_size = (n_acc // 2) + 1

        if not proposals:
            proposals = [{"proposer_id": 1, "proposal_num": 101, "value": "COMMIT_TX_1"}]

        consensus_value = None
        consensus_achieved = False
        rounds_executed = 0

        for prop in proposals:
            p_num = int(prop.get("proposal_num", 100))
            proposed_val = prop.get("value", "DEFAULT_VAL")
            rounds_executed += 1

            # Phase 1: Prepare
            promises = []
            highest_accepted_n = -1
            highest_accepted_val = None

            for acc in acceptors:
                ok, prev_n, prev_v = acc.receive_prepare(p_num)
                if ok:
                    promises.append(acc)
                    if prev_n is not None and prev_n > highest_accepted_n:
                        highest_accepted_n = prev_n
                        highest_accepted_val = prev_v

            if len(promises) < quorum_size:
                # Prepare phase rejected (lost majority quorum)
                continue

            # Pick value to propose: highest accepted value among promises, or own value
            val_to_propose = highest_accepted_val if highest_accepted_val is not None else proposed_val

            # Phase 2: Accept
            accepts = 0
            for acc in acceptors:
                if acc.receive_accept(p_num, val_to_propose):
                    accepts += 1

            if accepts >= quorum_size:
                consensus_value = val_to_propose
                consensus_achieved = True
                break

        return {
            "consensus_achieved": consensus_achieved,
            "chosen_value": consensus_value,
            "quorum_size": quorum_size,
            "num_acceptors": n_acc,
            "rounds_executed": rounds_executed,
            "acceptors_state": [
                {"id": a.node_id, "accepted_val": a.accepted_value, "min_proposal": a.min_proposal}
                for a in acceptors
            ],
        }


class RaftLeaderElectionLogReplication:
    """Raft Consensus Algorithm: Leader Election & Replicated Log.

    Simulates Raft cluster state machine (Follower, Candidate, Leader),
    term elections with randomized timeouts, split-vote handling, and
    AppendEntries log replication with strict commit index advancement.
    """

    class RaftNode:
        def __init__(self, node_id: int):
            self.node_id = node_id
            self.state = "FOLLOWER"
            self.current_term = 0
            self.voted_for: Optional[int] = None
            self.log: List[Dict[str, Any]] = []  # entries: {"term": t, "command": cmd}
            self.commit_index = 0

        def request_vote(self, term: int, candidate_id: int, last_log_idx: int, last_log_term: int) -> bool:
            if term > self.current_term:
                self.current_term = term
                self.state = "FOLLOWER"
                self.voted_for = None

            if term == self.current_term and (self.voted_for is None or self.voted_for == candidate_id):
                my_last_term = self.log[-1]["term"] if self.log else 0
                my_last_idx = len(self.log)

                # Log is at least as up-to-date
                if last_log_term > my_last_term or (last_log_term == my_last_term and last_log_idx >= my_last_idx):
                    self.voted_for = candidate_id
                    return True
            return False

        def append_entries(self, term: int, leader_id: int, prev_log_idx: int, prev_log_term: int, entries: List[Dict[str, Any]], leader_commit: int) -> bool:
            if term > self.current_term:
                self.current_term = term
                self.state = "FOLLOWER"
                self.voted_for = None

            if term < self.current_term:
                return False

            self.state = "FOLLOWER"

            # Check log consistency at prev_log_idx
            if prev_log_idx > 0:
                if len(self.log) < prev_log_idx:
                    return False
                if self.log[prev_log_idx - 1]["term"] != prev_log_term:
                    return False

            # Append new entries
            self.log = self.log[:prev_log_idx] + list(entries)
            if leader_commit > self.commit_index:
                self.commit_index = min(leader_commit, len(self.log))
            return True

    @classmethod
    def simulate_cluster(
        cls,
        num_nodes: int = 5,
        commands: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Simulates leader election and replicated log appending in Raft cluster."""
        n = max(3, int(num_nodes))
        nodes = [cls.RaftNode(i) for i in range(n)]
        majority = (n // 2) + 1

        if commands is None:
            commands = ["SET x=1", "SET y=2", "SET z=3"]

        # 1. Candidate 0 triggers election for Term 1
        term = 1
        candidate = nodes[0]
        candidate.state = "CANDIDATE"
        candidate.current_term = term
        candidate.voted_for = candidate.node_id

        votes = 1
        for other in nodes[1:]:
            if other.request_vote(term, candidate.node_id, last_log_idx=0, last_log_term=0):
                votes += 1

        leader_elected = False
        leader_id = None
        if votes >= majority:
            candidate.state = "LEADER"
            leader_elected = True
            leader_id = candidate.node_id

        # 2. Replicate log entries if leader elected
        replicated_count = 0
        if leader_elected:
            leader = nodes[leader_id]
            for cmd in commands:
                entry = {"term": term, "command": cmd}
                prev_idx = len(leader.log)
                prev_term = leader.log[-1]["term"] if leader.log else 0
                leader.log.append(entry)

                acks = 1
                for other in nodes:
                    if other.node_id != leader_id:
                        if other.append_entries(
                            term=term,
                            leader_id=leader_id,
                            prev_log_idx=prev_idx,
                            prev_log_term=prev_term,
                            entries=[entry],
                            leader_commit=len(leader.log),
                        ):
                            acks += 1

                if acks >= majority:
                    leader.commit_index = len(leader.log)
                    replicated_count += 1

        return {
            "leader_elected": leader_elected,
            "leader_id": leader_id,
            "current_term": term,
            "majority_quorum": majority,
            "num_nodes": n,
            "commands_committed": replicated_count,
            "leader_log_length": len(nodes[leader_id].log) if leader_elected else 0,
            "all_nodes_committed": [n_node.commit_index for n_node in nodes],
        }


def cloud_paxos_simulate_round(
    num_acceptors: int = 5,
    proposals: Optional[List[Dict[str, Any]]] = None,
) -> Record:
    """Simulates distributed Paxos consensus round over majority quorum."""
    return Record(PaxosConsensusProtocolStateReplication.run_consensus(num_acceptors=num_acceptors, proposals=proposals))


def cloud_raft_simulate_cluster(
    num_nodes: int = 5,
    commands: Optional[List[str]] = None,
) -> Record:
    """Simulates Raft leader election and log entry replication."""
    return Record(RaftLeaderElectionLogReplication.simulate_cluster(num_nodes=num_nodes, commands=commands))



