"""Unit and integration tests for Cloud & Object Storage domain (use cloud)."""

import os
import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.cloud.runtime import (
    CloudBucket,
    connect_to_bucket,
    upload_cloud_file,
    download_cloud_file,
    list_cloud_files,
    generate_cloud_signed_url,
)


def test_cloud_runtime_direct(tmp_path):
    bucket = connect_to_bucket("test-vault")

    # Create dummy local file
    sample_file = tmp_path / "hello.txt"
    sample_file.write_text("Hello Cloud Storage!", encoding="utf-8")

    # Upload
    uploaded_path = upload_cloud_file(bucket, str(sample_file), "docs/hello.txt")
    assert uploaded_path == "s3://test-vault/docs/hello.txt"

    # List
    all_files = list_cloud_files(bucket)
    assert "docs/hello.txt" in all_files

    txt_files = list_cloud_files(bucket, pattern="*.txt")
    assert "docs/hello.txt" in txt_files

    # Signed URL
    url = generate_cloud_signed_url(bucket, "docs/hello.txt", expiry=1800)
    assert url.startswith("https://test-vault.s3.amazonaws.com/docs/hello.txt?token=")

    # Download
    dest_file = tmp_path / "downloaded_hello.txt"
    download_cloud_file(bucket, "docs/hello.txt", str(dest_file))
    assert dest_file.exists()
    assert dest_file.read_text(encoding="utf-8") == "Hello Cloud Storage!"


def test_cloud_domain_script_execution(tmp_path):
    local_src = tmp_path / "raw.csv"
    local_src.write_text("id,val\n1,100\n2,200\n", encoding="utf-8")
    src_path = str(local_src).replace("\\", "/")

    dl_target = tmp_path / "restored.csv"
    dl_path = str(dl_target).replace("\\", "/")

    source = f"""use cloud

connect to bucket "analytics-data" into my_bucket
upload file "{src_path}" to bucket my_bucket as "datasets/raw.csv"
list all files in my_bucket matching "*.csv" into csv_list
generate signed url for "datasets/raw.csv" in my_bucket into presigned_link
download file "datasets/raw.csv" from bucket my_bucket to "{dl_path}"
"""
    env = execute(source)
    assert "datasets/raw.csv" in env["csv_list"]
    assert env["presigned_link"].startswith("https://analytics-data.s3.amazonaws.com/")
    assert dl_target.exists()
    assert "1,100" in dl_target.read_text(encoding="utf-8")


def test_cloud_domain_python_export():
    source = """use cloud

connect to bucket "storage-box" into b
upload file "input.json" to bucket b as "data/input.json"
list all files in b into files
"""
    py_code = export_to_python(source)
    assert "connect_to_bucket" in py_code
    assert "upload_cloud_file" in py_code
    assert "list_cloud_files" in py_code
