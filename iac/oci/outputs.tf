output "vm_public_ip" {
  description = "The public IP address of the OCI VM"
  value       = oci_core_instance.codexrelic_vm.public_ip
}
