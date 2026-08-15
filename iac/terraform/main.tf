terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 4.0.0"
    }
  }
}

provider "oci" {
  tenancy_ocid = var.tenancy_ocid
  user_ocid    = var.user_ocid
  fingerprint  = var.fingerprint
  private_key  = var.private_key
  region       = var.region
}

# VCN and Subnets for OKE
module "vcn" {
  source  = "oracle-terraform-modules/vcn/oci"
  version = "3.6.0"
  
  compartment_id = var.compartment_id
  region         = var.region

  
  vcn_name      = "codexrelic-vcn"
  vcn_dns_label = "codexrelicvcn"
  vcn_cidrs     = ["10.0.0.0/16"]
  
  create_internet_gateway = true
  create_nat_gateway      = true
  create_service_gateway  = true
}

# OKE Cluster (Always Free Ampere A1 Compute)
resource "oci_containerengine_cluster" "k8s_cluster" {
  compartment_id     = var.compartment_id
  kubernetes_version = "v1.28.2"
  name               = "codexrelic-oke"
  vcn_id             = module.vcn.vcn_id
  
  endpoint_config {
    is_public_ip_enabled = true
    subnet_id            = module.vcn.ig_route_id
  }
  
  options {
    add_ons {
      is_kubernetes_dashboard_enabled = false
      is_tiller_enabled               = false
    }
    admission_controller_options {
      is_pod_security_policy_enabled = false
    }
  }
}

resource "oci_containerengine_node_pool" "k8s_node_pool" {
  cluster_id         = oci_containerengine_cluster.k8s_cluster.id
  compartment_id     = var.compartment_id
  kubernetes_version = "v1.28.2"
  name               = "codexrelic-pool"
  
  node_shape = "VM.Standard.A1.Flex"
  
  node_shape_config {
    ocpus         = 2 
    memory_in_gbs = 12 
  }
  
  node_config_details {
    placement_configs {
      availability_domain = var.availability_domain
      subnet_id           = module.vcn.nat_route_id
    }
    size = 1
  }
}
