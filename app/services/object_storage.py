"""Object Storage adapters for local testing and OCI deployment."""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.core.config import settings


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
        del content_type
        target = (self.root / self.bucket / object_key).resolve()
        if self.root not in target.parents:
            raise ValueError("Object key escapes the configured storage root.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        digest = hashlib.sha256(content).hexdigest()
        return StoredObject(self.bucket, object_key, digest, digest)


class OCIObjectStorage:
    def __init__(self, bucket: str, namespace: str, region: str, use_instance_principal: bool = True):
        import oci

        self.bucket = bucket
        self.namespace = namespace
        if use_instance_principal:
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            self.client = oci.object_storage.ObjectStorageClient({"region": region}, signer=signer)
        else:
            config = oci.config.from_file()
            self.client = oci.object_storage.ObjectStorageClient(config)

    def put(self, object_key: str, content: bytes, content_type: str) -> StoredObject:
        response = self.client.put_object(self.namespace, self.bucket, object_key, content, content_type=content_type)
        digest = hashlib.sha256(content).hexdigest()
        return StoredObject(self.bucket, object_key, response.headers.get("etag", "").strip('"'), digest)


def configured_storage() -> ObjectStorage:
    if settings.storage_backend == "local":
        return LocalObjectStorage(settings.local_storage_path, settings.storage_bucket)
    if settings.storage_backend == "oci":
        if not settings.oci_namespace or not settings.oci_region:
            raise RuntimeError("OCI_NAMESPACE and OCI_REGION are required for OCI storage.")
        return OCIObjectStorage(settings.storage_bucket, settings.oci_namespace, settings.oci_region, settings.oci_use_instance_principal)
    raise RuntimeError(f"Unsupported STORAGE_BACKEND: {settings.storage_backend}")
