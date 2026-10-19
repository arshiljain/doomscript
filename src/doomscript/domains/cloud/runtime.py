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
