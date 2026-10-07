data "oci_identity_compartments" "accessible" {
  compartment_id            = var.tenancy_ocid
  compartment_id_in_subtree = true
  access_level              = "ACCESSIBLE"
  state                     = "ACTIVE"
}

locals {
  matching_compartments = [for compartment in data.oci_identity_compartments.accessible.compartments : compartment.id if compartment.name == var.compartment_name]
  compartment_ocid      = coalesce(var.compartment_ocid, try(local.matching_compartments[0], null), var.tenancy_ocid)
}

data "oci_identity_availability_domains" "available" {
  compartment_id = local.compartment_ocid
}

data "oci_core_images" "oracle_linux_arm" {
  compartment_id   = local.compartment_ocid
  operating_system = "Oracle Linux"
  sort_by          = "TIMECREATED"
  sort_order       = "DESC"

  filter {
    name   = "display_name"
    values = ["^Oracle-Linux-.*-aarch64-.*$"]
    regex  = true
  }
}

data "oci_objectstorage_namespace" "current" {}

locals {
  availability_domain = coalesce(var.availability_domain, data.oci_identity_availability_domains.available.availability_domains[0].name)
  image_ocid          = var.image_ocid != null ? var.image_ocid : data.oci_core_images.oracle_linux_arm.images[0].id
}

resource "oci_core_vcn" "communitylab" {
  compartment_id = local.compartment_ocid
  cidr_blocks    = ["10.20.0.0/16"]
  display_name   = "communitylab-vcn"
  dns_label      = "communitylab"
}

resource "oci_core_internet_gateway" "communitylab" {
  compartment_id = local.compartment_ocid
  vcn_id         = oci_core_vcn.communitylab.id
  enabled        = true
  display_name   = "communitylab-igw"
}

resource "oci_core_route_table" "public" {
  compartment_id = local.compartment_ocid
  vcn_id         = oci_core_vcn.communitylab.id
  route_rules {
    network_entity_id = oci_core_internet_gateway.communitylab.id
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
  }
}

resource "oci_core_security_list" "public" {
  compartment_id = local.compartment_ocid
  vcn_id         = oci_core_vcn.communitylab.id
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
  ingress_security_rules {
    protocol = "6"
    source   = var.ssh_source_cidr
    tcp_options {
      min = 22
      max = 22
    }
  }
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 80
      max = 80
    }
  }
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 443
      max = 443
    }
  }
}

resource "oci_core_subnet" "public" {
  compartment_id             = local.compartment_ocid
  vcn_id                     = oci_core_vcn.communitylab.id
  cidr_block                 = "10.20.1.0/24"
  display_name               = "communitylab-public"
  dns_label                  = "public"
  route_table_id             = oci_core_route_table.public.id
  security_list_ids          = [oci_core_security_list.public.id]
  prohibit_public_ip_on_vnic = false
}

resource "oci_core_instance" "communitylab" {
  availability_domain = local.availability_domain
  compartment_id      = local.compartment_ocid
  display_name        = "communitylab-free"
  shape               = var.instance_shape
  shape_config {
    ocpus         = var.ocpus
    memory_in_gbs = var.memory_in_gbs
  }
  create_vnic_details {
    subnet_id        = oci_core_subnet.public.id
    assign_public_ip = true
    hostname_label   = "app"
  }
  source_details {
    source_type             = "image"
    source_id               = local.image_ocid
    boot_volume_size_in_gbs = 50
  }
  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(file("${path.module}/cloud-init.yaml"))
  }
}

resource "oci_identity_dynamic_group" "communitylab" {
  compartment_id = var.tenancy_ocid
  name           = "communitylab-free-instance"
  description    = "CommunityLab OCI Free Tier application instance"
  matching_rule  = "instance.id = '${oci_core_instance.communitylab.id}'"
}

resource "oci_identity_policy" "communitylab_storage" {
  compartment_id = var.tenancy_ocid
  name           = "communitylab-free-storage"
  description    = "Allow the CommunityLab instance to publish approved assets"
  statements = [
    "Allow dynamic-group ${oci_identity_dynamic_group.communitylab.name} to read buckets in compartment id ${local.compartment_ocid}",
    "Allow dynamic-group ${oci_identity_dynamic_group.communitylab.name} to manage objects in compartment id ${local.compartment_ocid} where target.bucket.name = '${var.bucket_name}'"
  ]
}
