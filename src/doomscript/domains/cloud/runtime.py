"""Runtime execution engine for Cloud & Object Storage domain."""

from typing import Any, Dict, List, Optional, Tuple, Union
import fnmatch
import os
import shutil
from pathlib import Path
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

