output "public_ip" { value = oci_core_instance.communitylab.public_ip }
output "instance_id" { value = oci_core_instance.communitylab.id }
output "bucket_name" { value = var.bucket_name }
output "object_storage_namespace" { value = data.oci_objectstorage_namespace.current.namespace }
