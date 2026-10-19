"""Declarative specifications and Intermediate Representation for Cloud & Object Storage domain."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class CloudConnectSpec(DomainIR):
    bucket_name: str
    target_var: str = "bucket"
    provider: str = "s3"

    def validate(self) -> List[str]:
        errors = []
        if not self.bucket_name:
            errors.append("CloudConnectSpec requires a bucket name")
        return errors


@dataclass
class CloudUploadSpec(DomainIR):
    bucket_var: str
    local_path: str
    remote_path: str

    def validate(self) -> List[str]:
        errors = []
        if not self.local_path or not self.remote_path:
            errors.append("CloudUploadSpec requires both local_path and remote_path")
        return errors


@dataclass
class CloudDownloadSpec(DomainIR):
    bucket_var: str
    remote_path: str
    local_path: str

    def validate(self) -> List[str]:
        errors = []
        if not self.remote_path or not self.local_path:
            errors.append("CloudDownloadSpec requires both remote_path and local_path")
        return errors


@dataclass
class CloudListSpec(DomainIR):
    bucket_var: str
    target_var: str
    pattern: str = ""

    def validate(self) -> List[str]:
        return []


@dataclass
class CloudSignedUrlSpec(DomainIR):
    bucket_var: str
    remote_path: str
    target_var: str
    expiry_sec: int = 3600

    def validate(self) -> List[str]:
        return []
