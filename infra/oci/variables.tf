variable "compartment_ocid" {
  type        = string
  default     = null
  description = "Optional compartment OCID. The named compartment is discovered when omitted."
}

variable "tenancy_ocid" {
  type        = string
  description = "Tenancy OCID used to create the instance dynamic group."
}

variable "availability_domain" {
  type        = string
  default     = null
  description = "Optional availability domain. The first available domain is used when omitted."
}

variable "image_ocid" {
  type        = string
  default     = null
  description = "Optional Oracle Linux ARM image OCID. The newest compatible image is used when omitted."
}

variable "ssh_public_key" {
  type      = string
  sensitive = true
}

variable "region" {
  type    = string
  default = "sa-saopaulo-1"
}

variable "instance_shape" {
  type    = string
  default = "VM.Standard.A1.Flex"
}

variable "ocpus" {
  type    = number
  default = 1
}

variable "memory_in_gbs" {
  type    = number
  default = 6
}

variable "ssh_source_cidr" {
  type        = string
  description = "Administrator public IP as x.x.x.x/32."
}

variable "bucket_name" {
  type        = string
  default     = "CommunityLab-Bucket"
  description = "Existing private Object Storage bucket used for approved assets."
}

variable "compartment_name" {
  type        = string
  default     = "CommunityLab"
  description = "Compartment name to discover when compartment_ocid is omitted."
}
