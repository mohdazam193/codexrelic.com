# ──────────────────────────────────────────────────────────────────
# OCI Always Free ARM Instance (VM.Standard.A1.Flex)
#
# Capacity Strategy:
#   OCI frequently reports "Out of Host Capacity" for ARM instances.
#   We try all 3 Fault Domains within the Availability Domain using
#   count + index cycling. Terraform picks the one that succeeds.
#   If all fail, the retry loop in the pipeline keeps trying.
# ──────────────────────────────────────────────────────────────────

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

# Fetch all fault domains in the selected Availability Domain
data "oci_identity_fault_domains" "fds" {
  compartment_id      = var.compartment_id
  availability_domain = var.availability_domain
}

data "oci_core_images" "ubuntu" {
  compartment_id           = var.compartment_id
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "22.04"
  shape                    = "VM.Standard.A1.Flex"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_instance" "codexrelic_vm" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_id
  shape               = "VM.Standard.A1.Flex"
  display_name        = "codexrelic-vm"

  # Cycle through all available fault domains to maximize chance of
  # finding a slot when OCI is under capacity pressure.
  # fault_domain is optional — OCI will pick one if omitted, but
  # specifying it increases predictability for retries.
  fault_domain = data.oci_identity_fault_domains.fds.fault_domains[var.fault_domain_index].name

  shape_config {
    ocpus         = 2
    memory_in_gbs = 12
  }

  source_details {
    source_type             = "image"
    source_id               = data.oci_core_images.ubuntu.images[0].id
    boot_volume_size_in_gbs = 50
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.codexrelic_subnet.id
    assign_public_ip = true
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
  }

  timeouts {
    create = "30m"
  }
}
