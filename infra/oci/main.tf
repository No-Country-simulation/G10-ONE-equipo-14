resource "oci_core_vcn" "communitylab" {
  compartment_id = var.compartment_ocid
  cidr_blocks     = ["10.20.0.0/16"]
  display_name    = "communitylab-vcn"
  dns_label       = "communitylab"
}

resource "oci_core_internet_gateway" "communitylab" {
  compartment_id = var.compartment_ocid
  vcn_id          = oci_core_vcn.communitylab.id
  enabled         = true
  display_name    = "communitylab-igw"
}

resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid
  vcn_id          = oci_core_vcn.communitylab.id
  route_rules { network_entity_id = oci_core_internet_gateway.communitylab.id; destination = "0.0.0.0/0"; destination_type = "CIDR_BLOCK" }
}

resource "oci_core_security_list" "public" {
  compartment_id = var.compartment_ocid
  vcn_id          = oci_core_vcn.communitylab.id
  egress_security_rules { protocol = "all"; destination = "0.0.0.0/0" }
  ingress_security_rules { protocol = "6"; source = var.ssh_source_cidr; tcp_options { min = 22; max = 22 } }
  ingress_security_rules { protocol = "6"; source = "0.0.0.0/0"; tcp_options { min = 80; max = 80 } }
  ingress_security_rules { protocol = "6"; source = "0.0.0.0/0"; tcp_options { min = 443; max = 443 } }
}

resource "oci_core_subnet" "public" {
  compartment_id             = var.compartment_ocid
  vcn_id                      = oci_core_vcn.communitylab.id
  cidr_block                  = "10.20.1.0/24"
  display_name                = "communitylab-public"
  dns_label                   = "public"
  route_table_id              = oci_core_route_table.public.id
  security_list_ids           = [oci_core_security_list.public.id]
  prohibit_public_ip_on_vnic  = false
}

resource "oci_core_instance" "communitylab" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_ocid
  display_name        = "communitylab-free"
  shape               = var.instance_shape
  shape_config { ocpus = var.ocpus; memory_in_gbs = var.memory_in_gbs }
  create_vnic_details { subnet_id = oci_core_subnet.public.id; assign_public_ip = true; hostname_label = "app" }
  source_details { source_type = "image"; source_id = var.image_ocid; boot_volume_size_in_gbs = 50 }
  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data = base64encode(file("${path.module}/cloud-init.yaml"))
  }
}
