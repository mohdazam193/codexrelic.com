resource "oci_core_vcn" "codexrelic_vcn" {
  compartment_id = var.compartment_id
  cidr_blocks    = ["10.0.0.0/16"]
  display_name   = "codexrelic-vcn"
  dns_label      = "codexrelicvcn"
}

resource "oci_core_internet_gateway" "codexrelic_igw" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.codexrelic_vcn.id
  display_name   = "codexrelic-igw"
  enabled        = true
}

resource "oci_core_default_route_table" "codexrelic_rt" {
  manage_default_resource_id = oci_core_vcn.codexrelic_vcn.default_route_table_id
  display_name               = "codexrelic-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.codexrelic_igw.id
  }
}

resource "oci_core_default_security_list" "codexrelic_sl" {
  manage_default_resource_id = oci_core_vcn.codexrelic_vcn.default_security_list_id
  display_name               = "codexrelic-sl"

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 22
      min = 22
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 80
      min = 80
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 443
      min = 443
    }
  }
}

resource "oci_core_subnet" "codexrelic_subnet" {
  compartment_id             = var.compartment_id
  vcn_id                     = oci_core_vcn.codexrelic_vcn.id
  cidr_block                 = "10.0.1.0/24"
  display_name               = "codexrelic-subnet"
  dns_label                  = "subnet"
  prohibit_public_ip_on_vnic = false
}
