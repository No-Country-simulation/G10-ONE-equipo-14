variable "compartment_ocid" { type = string }
variable "availability_domain" { type = string }
variable "image_ocid" { type = string; description = "Oracle Linux ARM image OCID for the selected region." }
variable "ssh_public_key" { type = string; sensitive = true }
variable "region" { type = string; default = "sa-saopaulo-1" }
variable "instance_shape" { type = string; default = "VM.Standard.A1.Flex" }
variable "ocpus" { type = number; default = 1 }
variable "memory_in_gbs" { type = number; default = 6 }
variable "ssh_source_cidr" { type = string; description = "Administrator public IP as x.x.x.x/32." }
