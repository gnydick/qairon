locals {
  # if !cluster, then node_count = replica cluster_size, if cluster then node_count = shard*(replica + 1)
  # Why doing this 'The "count" value depends on resource attributes that cannot be determined until apply'. So pre-calculating
  member_clusters_count = (var.cluster_mode_enabled
  ?
  (var.cluster_mode_num_node_groups * (var.cluster_mode_replicas_per_node_group + 1))
  :
  var.cluster_size
  )
}