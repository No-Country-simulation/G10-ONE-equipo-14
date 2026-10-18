"""Object Storage adapters for local testing and OCI deployment."""

import hashlib
import logging
from time import perf_counter
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.core.config import settings
from app.core.observability import log_event

logger = logging.getLogger("communitylab.storage")


@dataclass(frozen=True)
class StoredObject:
    bucket: str
    object_key: str
    etag: str
    sha256: str


class ObjectStorage(Protocol):
    def put(self, object_key: str, content: bytes, content_type: str) -> StoredObject: ...


class LocalObjectStorage:
    def __init__(self, root: str, bucket: str):
        self.root = Path(root).resolve()
        self.bucket = bucket

    def put(self, object_key: str, content: bytes, content_type: str) -> StoredObject:
        started = perf_counter()
        del content_type
        target = (self.root / self.bucket / object_key).resolve()
        if self.root not in target.parents:
            raise ValueError("Object key escapes the configured storage root.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        digest = hashlib.sha256(content).hexdigest()
        stored = StoredObject(self.bucket, object_key, digest, digest)
        log_event(logger, "storage_put_completed", backend="local", bucket=self.bucket, bytes=len(content), duration_ms=round((perf_counter() - started) * 1000, 2))
        return stored


class OCIObjectStorage:
    def __init__(
        self,
        bucket: str,
        namespace: str,
        region: str,
        use_instance_principal: bool = True,
        config_file: str | None = None,
    ):
        import oci

        self.bucket = bucket
        self.namespace = namespace
        if use_instance_principal:
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            self.client = oci.object_storage.ObjectStorageClient({"region": region}, signer=signer)
        else:
            if config_file:
                config = oci.config.from_file(file_location=config_file)
            else:
                config = oci.config.from_file()
            config["region"] = region
            self.client = oci.object_storage.ObjectStorageClient(config)

    def put(self, object_key: str, content: bytes, content_type: str) -> StoredObject:
        started = perf_counter()
        response = self.client.put_object(self.namespace, self.bucket, object_key, content, content_type=content_type)
        digest = hashlib.sha256(content).hexdigest()
        stored = StoredObject(self.bucket, object_key, response.headers.get("etag", "").strip('"'), digest)
        log_event(logger, "storage_put_completed", backend="oci", bucket=self.bucket, bytes=len(content), duration_ms=round((perf_counter() - started) * 1000, 2))
        return stored


def configured_storage() -> ObjectStorage:
    if settings.storage_backend == "local":
        return LocalObjectStorage(settings.local_storage_path, settings.storage_bucket)
    if settings.storage_backend == "oci":
        if not settings.oci_namespace or not settings.oci_region:
            raise RuntimeError("OCI_NAMESPACE and OCI_REGION are required for OCI storage.")
        return OCIObjectStorage(
            settings.storage_bucket,
            settings.oci_namespace,
            settings.oci_region,
            settings.oci_use_instance_principal,
            settings.oci_config_file,
        )
    raise RuntimeError(f"Unsupported STORAGE_BACKEND: {settings.storage_backend}")
