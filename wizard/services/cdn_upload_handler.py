"""
Simple CDN upload handler implementations.

Used by automation and CLI helpers that mirror local asset caches (fonts, samples,
etc.) into S3-backed CDNs. Right now the handler is scoped to AWS S3 but the API
is intentionally small so future providers (Akamai, Cloudflare R2) can be added.
"""

import logging
import os
from pathlib import Path
from typing import Iterable, Optional

try:
    import boto3  # boto3 is optional; handler will raise if missing
    from botocore.exceptions import ClientError
except ImportError:  # pragma: no cover - optional runtime dependency
    boto3 = None  # type: ignore
    ClientError = Exception  # type: ignore

logger = logging.getLogger("cdn-upload")


class CdnUploadHandler:
    """Upload files & directories to a CDN-backed S3 bucket."""

    def __init__(
        self,
        bucket: str,
        local_root: Path,
        remote_prefix: str = "",
        region: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        if boto3 is None:
            raise RuntimeError("Install boto3 to use the CDN upload handler.")
        self.bucket = bucket
        self.local_root = local_root.expanduser().resolve()
        self.remote_prefix = remote_prefix.strip("/ ")
        session_args = {}
        if profile:
            session_args["profile_name"] = profile
        session = boto3.Session(**session_args)
        client_args = {}
        if region:
            client_args["region_name"] = region
        if access_key and secret_key:
            client_args["aws_access_key_id"] = access_key
            client_args["aws_secret_access_key"] = secret_key
        self.client = session.client("s3", **client_args)

    def upload_file(self, path: Path, key: Optional[str] = None) -> None:
        """Upload a single file to the CDN bucket."""
        relative = path.relative_to(self.local_root)
        destination = (
            f"{self.remote_prefix}/{key or relative.as_posix()}"
            if self.remote_prefix
            else key or relative.as_posix()
        )
        logger.info("Uploading %s to s3://%s/%s", path, self.bucket, destination)
        try:
            self.client.upload_file(str(path), self.bucket, destination)
        except ClientError as exc:
            logger.error("Failed to upload %s: %s", path, exc)
            raise

    def sync_directory(
        self, include: Optional[Iterable[str]] = None, exclude: Optional[Iterable[str]] = None
    ) -> None:
        """
        Walk the local root and upload all files, optionally filtering by include/exclude globs.
        """
        include = set(include or [])
        exclude = set(exclude or [])
        for root, _, files in os.walk(self.local_root):
            base = Path(root)
            for name in files:
                path = base / name
                rel = path.relative_to(self.local_root)
                if include and rel.as_posix() not in include:
                    continue
                if exclude and rel.as_posix() in exclude:
                    continue
                self.upload_file(path)

    @classmethod
    def from_env(cls) -> "CdnUploadHandler":
        """Helper that builds the handler from environment variables."""
        bucket = os.environ.get("UDOS_CDN_BUCKET")
        if not bucket:
            raise RuntimeError("UDOS_CDN_BUCKET is required for CDN uploads.")
        root = Path(os.environ.get("UDOS_CDN_ROOT", "~/uDOS"))
        return cls(
            bucket=bucket,
            local_root=root,
            remote_prefix=os.environ.get("UDOS_CDN_PREFIX", ""),
            region=os.environ.get("UDOS_CDN_REGION"),
            access_key=os.environ.get("UDOS_CDN_ACCESS_KEY"),
            secret_key=os.environ.get("UDOS_CDN_SECRET_KEY"),
            profile=os.environ.get("UDOS_CDN_PROFILE"),
        )
