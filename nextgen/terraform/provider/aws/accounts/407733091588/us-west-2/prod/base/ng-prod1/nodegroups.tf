locals {
  key_name = "${var.region}-${var.key_name}"
}


module "infra_svcs_stack" {
  source = "../../../../../../../../modules/cloudformation-20190211"
  azs = "${var.azs}"
  ami = "${var.infra_nodegroup_ami}"
  vpc_id = "${var.vpc_id}"
  config_name = "${var.config_name}"
  key_name = "${local.key_name}"
  cp_sg_id = "${var.cp_sg_id}"
  region = "${var.region}"
  role = "infrasvcs"
  environment = "${var.environment}"
  node_volume_size = "${var.node_volume_size}"
  extra_tags = {}
  node_instance_type = "${var.infra_instance_type}"
  subnets = "${join(",", "${var.private_subnet_ids}")}"
  node_auto_scaling_group_desired_capacity = "${var.infra_scaling_desired_capacity}"
  group_number = "1"
  min_size = "${var.infra_min_size}"
  max_size = "${var.infra_max_size}"
  bootstrap_arguments = "${var.infra_bootstrap_arguments}"
  deployment_target = "${var.deployment_target}"
  cluster_name = "${module.cluster.cluster_name}"
  nodegroup_number = "${var.nodegroup_number}"
  proxy_security_group = "${module.proxy_sg.sg_id}"
}

module "foo_svcs_stack" {
  source = "../../../../../../../../modules/cloudformation-20190211"
  azs = "${var.azs}"
  ami = "${var.foo_nodegroup_ami}"
  vpc_id = "${var.vpc_id}"
  config_name = "${var.config_name}"
  key_name = "${var.region}-${var.key_name}"
  cp_sg_id = "${var.cp_sg_id}"
  region = "${var.region}"
  role = "foosvcs"
  environment = "${var.environment}"
  node_volume_size = "${var.node_volume_size}"
  extra_tags = {}
  node_instance_type = "${var.foo_instance_type}"
  subnets = "${join(",", "${var.private_subnet_ids}")}"
  node_auto_scaling_group_desired_capacity = "${var.foo_scaling_desired_capacity}"
  group_number = "1"
  min_size = "${var.foo_min_size}"
  max_size = "${var.foo_max_size}"
  bootstrap_arguments = "${var.foo_bootstrap_arguments}"
  deployment_target = "${var.deployment_target}"
  cluster_name = "${module.cluster.cluster_name}"
  nodegroup_number = "${var.nodegroup_number}"
  proxy_security_group = "${module.proxy_sg.sg_id}"
}


module "infra_svcs-foo_svcs-peering" {
  source = "../../../../../../../../modules/nodegroup-pair-sgs"
  nodegroup_a_id = "${module.infra_svcs_stack.security_group_id}"
  nodegroup_b_id = "${module.foo_svcs_stack.security_group_id}"
  nodegroup_a_name = "${module.infra_svcs_stack.nodegroup_name}"
  nodegroup_b_name = "${module.foo_svcs_stack.nodegroup_name}"

}

