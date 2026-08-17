variable "tenancy_ocid" {
  type        = string
  description = "The tenancy OCID"
}

variable "user_ocid" {
  type        = string
  description = "The user OCID"
}

variable "fingerprint" {
  type        = string
  description = "The fingerprint of the OCI API signing key"
}

variable "private_key_path" {
  type        = string
  description = "Path to the OCI API signing private key PEM file (written by pipeline)"
}

variable "region" {
  type        = string
  description = "The OCI region (e.g. ap-hyderabad-1)"
}

variable "compartment_id" {
  type        = string
  description = "The compartment OCID to deploy resources into"
}

variable "availability_domain" {
  type        = string
  description = "The availability domain (e.g. NjdN:AP-HYDERABAD-1-AD-1)"
}

variable "ssh_public_key" {
  type        = string
  description = "The SSH public key to inject into the VM for login"
}

variable "fault_domain_index" {
  type        = number
  description = "Index of the fault domain to try (0, 1, or 2). Cycle through all 3 if capacity fails."
  default     = 0
}
