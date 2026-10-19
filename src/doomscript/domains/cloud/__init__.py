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
from doomscript.domains.cloud.exporter import CloudASTExporter
from doomscript.domains.registry import get_domain_registry


class CloudDomain(DomainContract):
    """Cloud & Object Storage domain pack."""

    name = "cloud"
    aliases = ["s3", "storage", "bucket"]
    parser = CloudDomainParser()
    runtime = CloudRuntime()
    exporter = CloudASTExporter()

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
