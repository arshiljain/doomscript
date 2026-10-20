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
    cloud_list_prefix,
    cloud_sync_directory,
    cloud_file_metadata,
    cloud_file_exists,
    cloud_delete_matching,
    cloud_bucket_size,
    cloud_copy_object,
    cloud_generate_presigned_put_url,
    cloud_verify_md5_checksum,
    cloud_verify_sha256_checksum,
    cloud_set_object_tags,
    cloud_get_object_tags,
    cloud_batch_delete_keys,
    cloud_filter_files_by_size,
    cloud_filter_files_by_date,
    cloud_create_directory_marker,
    cloud_move_object,
    cloud_mirror_buckets,
    cloud_archive_stale_files,
    cloud_export_bucket_manifest,
    cloud_diff_buckets,
    cloud_count_objects_by_extension,
    cloud_read_object_text,
    cloud_write_object_text,
    cloud_get_storage_class,
    cloud_set_storage_class,
    CloudStorageManager,
    IAMPolicyEngine,
    CloudCostCalculator,
    MultipartUploadManager,
    ContentAddressableStorage,
    BucketLifecycleEngine,
    cloud_multipart_initiate,
    cloud_cas_put,
    cloud_evaluate_lifecycle,
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
            or s.startswith("sync directory ")
            or s.startswith("get metadata of file ")
            or s.startswith("check if file ")
            or s.startswith("delete files matching ")
            or s.startswith("calculate total size of ")
            or s.startswith("copy object ")
            or s.startswith("generate presigned put url ")
            or s.startswith("verify md5 checksum of ")
            or s.startswith("verify sha256 checksum of ")
            or s.startswith("set object tags for ")
            or s.startswith("get object tags for ")
            or s.startswith("batch delete keys ")
            or s.startswith("filter files in ")
            or s.startswith("create directory marker ")
            or s.startswith("move object ")
            or s.startswith("mirror bucket ")
            or s.startswith("archive stale files in ")
            or s.startswith("export manifest for ")
            or s.startswith("export bucket manifest for ")
            or s.startswith("diff bucket ")
            or s.startswith("diff buckets ")
            or s.startswith("count objects by extension in ")
            or (s.startswith("write ") and " to object " in s)
            or (s.startswith("write text ") and " in " in s)
            or (s.startswith("write object text ") and " to " in s)
            or (s.startswith("read ") and " from object " in s)
            or (s.startswith("read text ") and " in " in s)
            or (s.startswith("read object text ") and " from " in s)
            or s.startswith("get storage class ")
            or s.startswith("set storage class ")
        ):
            return True

        if s.startswith("upload file ") and (" to bucket " in s or (" to " in s and " as " in s)):
            return True
        if s.startswith("download file ") and (" from bucket " in s or (" from " in s and " to " in s)):
            return True
        if s.startswith("list all files in ") and " into " in s:
            return True
        if s.startswith("list files in ") and " with prefix " in s and " into " in s:
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
    "cloud_list_prefix",
    "cloud_sync_directory",
    "cloud_file_metadata",
    "cloud_file_exists",
    "cloud_delete_matching",
    "cloud_bucket_size",
    "cloud_copy_object",
    "cloud_generate_presigned_put_url",
    "cloud_verify_md5_checksum",
    "cloud_verify_sha256_checksum",
    "cloud_set_object_tags",
    "cloud_get_object_tags",
    "cloud_batch_delete_keys",
    "cloud_filter_files_by_size",
    "cloud_filter_files_by_date",
    "cloud_create_directory_marker",
    "cloud_move_object",
    "cloud_mirror_buckets",
    "cloud_archive_stale_files",
    "cloud_export_bucket_manifest",
    "cloud_diff_buckets",
    "cloud_count_objects_by_extension",
    "cloud_read_object_text",
    "cloud_write_object_text",
    "cloud_get_storage_class",
    "cloud_set_storage_class",
    "CloudStorageManager",
    "IAMPolicyEngine",
    "CloudCostCalculator",
    "MultipartUploadManager",
    "ContentAddressableStorage",
    "BucketLifecycleEngine",
    "cloud_multipart_initiate",
    "cloud_cas_put",
    "cloud_evaluate_lifecycle",
]
