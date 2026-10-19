"""Cloud & Object Storage Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.cloud.spec import (
    CloudConnectSpec,
    CloudUploadSpec,
    CloudDownloadSpec,
    CloudListSpec,
    CloudSignedUrlSpec,
)
from doomscript.domains.cloud.parser import CloudDomainParser
from doomscript.domains.cloud.runtime import (
    CloudBucket,
    CloudRuntime,
    connect_to_bucket,
    upload_cloud_file,
    download_cloud_file,
    list_cloud_files,
    generate_cloud_signed_url,
    execute_cloud_ir,
)
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.cloud.exporter import CloudASTExporter
from doomscript.domains.registry import get_domain_registry


class CloudDomain(DomainContract):
    """Cloud & Object Storage domain pack."""

    name = "cloud"
    aliases = ["s3", "storage", "bucket"]
    description = "Cloud & Object Storage operations for S3 and compatible blob stores"
    parser = CloudDomainParser()
    runtime = CloudRuntime()
    exporter = CloudASTExporter()
    capabilities = ["bucket", "upload", "download", "list", "signed_url"]
    optional_dependencies = ["boto3"]

    verbs = [
        VerbSpec(
            name="connect_bucket",
            pattern="connect to bucket {name:expr} (as|into) {target:ident}",
            arg_schema={"name": "expr", "target": "ident"},
            returns="Bucket",
            description="Establish connection to named cloud storage bucket",
        ),
        VerbSpec(
            name="upload_file",
            pattern="upload file {local_expr:expr} to [bucket] {b_var:ident} as {remote_expr:expr}",
            arg_schema={"local_expr": "expr", "b_var": "ident", "remote_expr": "expr"},
            returns="None",
            description="Upload local file to object storage path",
        ),
        VerbSpec(
            name="download_file",
            pattern="download file {remote_expr:expr} from [bucket] {b_var:ident} to {local_expr:expr}",
            arg_schema={"remote_expr": "expr", "b_var": "ident", "local_expr": "expr"},
            returns="None",
            description="Download remote object from bucket to local disk",
        ),
        VerbSpec(
            name="list_files",
            pattern="list all files in [bucket] {b_var:ident} [matching {pat:expr}] into {target:ident}",
            arg_schema={"b_var": "ident", "target": "ident"},
            returns="Collection",
            description="List keys matching prefix or pattern in bucket",
        ),
        VerbSpec(
            name="signed_url",
            pattern="generate signed url for {remote_expr:expr} in [bucket] {b_var:ident} [with expiry {sec:int} seconds] into {target:ident}",
            arg_schema={"remote_expr": "expr", "b_var": "ident", "sec": "int", "target": "ident"},
            defaults={"sec": 3600},
            returns="str",
            description="Generate pre-signed URL for direct browser access",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        if (
            s.startswith("connect to bucket ")
            or s.startswith("generate signed url ")
        ):
            return True

        if s.startswith("upload file ") and (" to bucket " in s or (" to " in s and " as " in s)):
            return True
        if s.startswith("download file ") and (" from bucket " in s or (" from " in s and " to " in s)):
            return True
        if s.startswith("list all files in ") and " into " in s:
            return True

        return False

    def can_handle_block(self, header: str) -> bool:
        return False


# Register with central registry
CLOUD_DOMAIN = CloudDomain()
get_domain_registry().register(CLOUD_DOMAIN)

__all__ = [
    "CloudDomain",
    "CLOUD_DOMAIN",
    "CloudConnectSpec",
    "CloudUploadSpec",
    "CloudDownloadSpec",
    "CloudListSpec",
    "CloudSignedUrlSpec",
    "CloudDomainParser",
    "CloudRuntime",
    "CloudASTExporter",
    "CloudBucket",
    "connect_to_bucket",
    "upload_cloud_file",
    "download_cloud_file",
    "list_cloud_files",
    "generate_cloud_signed_url",
    "execute_cloud_ir",
]
