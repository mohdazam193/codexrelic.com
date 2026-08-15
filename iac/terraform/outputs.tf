output "cluster_id" {
  description = "The OCID of the OKE cluster"
  value       = oci_containerengine_cluster.k8s_cluster.id
}

output "node_pool_id" {
  description = "The OCID of the Node Pool"
  value       = oci_containerengine_node_pool.k8s_node_pool.id
}

output "vcn_id" {
  description = "The OCID of the VCN"
  value       = module.vcn.vcn_id
}
