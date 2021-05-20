module "elasticache-microservices" {
  source = "../../../../../../../../modules/aws/elasticache"
  allowed_cidr_blocks = []
  allowed_security_groups = [module.cluster.nodes_security_group_id]
  apply_immediately = false
  automatic_failover_enabled = true
  availability_zones = var.azs
  cluster_mode_enabled = true
  cluster_mode_num_node_groups = 3
  cluster_mode_replicas_per_node_group = 2
  cluster_size = 0
  egress_cidr_blocks = ["0.0.0.0/0"]
  elasticache_subnet_group_name = "${var.environment}-elascticache"
  engine_version = "5.0.6"
  existing_security_groups = []
  instance_type = "cache.t3.medium"
  maintenance_window = "sat:07:00-sat:08:00"
  multi_az_enabled = true
  port = 11211
  replication_group_description = "${var.environment} replication group"
  replication_group_id = "${var.environment}-elascticache-rg"
  security_group_name = "${var.environment}-elasticache"
  snapshot_retention_limit = 10
  snapshot_window = "00:00-03:00"
  subnets = var.private_subnets_ids
  tags = {
    "GeneratedBy" = "terraform"
    "Environment"= var.environment
  }
  use_existing_security_groups = false
  vpc_id = var.vpc_id
  depends_on = [module.cluster]
}