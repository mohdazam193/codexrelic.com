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
  description = "The fingerprint of the API key"
}

variable "private_key" {
  type        = string
  description = "The raw private key content"
}

variable "region" {
  type        = string
  description = "The OCI region (e.g. us-ashburn-1)"
}

variable "compartment_ocid" {
  type        = string
  description = "The compartment OCID to deploy resources into"
}

variable "ssh_public_key" {
  type        = string
  description = "The SSH public key to inject into the VM"
}
