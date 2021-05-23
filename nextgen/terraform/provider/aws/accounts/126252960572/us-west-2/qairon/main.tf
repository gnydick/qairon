locals {
  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_ids["vpc0"]
}

module "db" {
  source = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 3.0"
  allowed_security_groups = [data.terraform_remote_state.vpc.outputs.eks_node_sg_ids["vpc0"]["infra0"]]
  name = "qairon-infra0"
  engine = "aurora-postgresql"
  engine_version = "10.14"
  instance_type = "db.t3.large"

  vpc_id = local.vpc_id
  subnets = data.terraform_remote_state.vpc.outputs.private_subnet_ids["vpc0"]["rds"]

  replica_count = 4

  storage_encrypted = true
  apply_immediately = true
  monitoring_interval = 10

  db_parameter_group_name = "default.aurora-postgresql10"
  db_cluster_parameter_group_name = "default.aurora-postgresql10"

  enabled_cloudwatch_logs_exports = ["postgresql"]


}


resource "aws_security_group_rule" "eks_out_to_rds" {
  from_port = 5432
  protocol = "tcp"
  security_group_id = data.terraform_remote_state.vpc.outputs.eks_node_sg_ids["vpc0"]["infra0"]
  to_port = 5432
  type = "egress"
  source_security_group_id = module.db.this_security_group_id
}