data "template_file" "amazon-eks-nodegroup_yaml" {
  template = "${file("${path.module}/amazon-eks-nodegroup.yaml")}"

}

locals {
  stack_name = "${var.environment}-${var.role}-${var.nodegroup_number}-stack"
  stack_tag_name = "${var.environment}.${var.deployment_target}.${var.role}.${var.nodegroup_number}.stack"
}


resource "aws_cloudformation_stack" "stack" {

  name = "${local.stack_name}"
  capabilities = [
    "CAPABILITY_IAM"]
  template_body = "${data.template_file.amazon-eks-nodegroup_yaml.rendered}"


  parameters {
    BootstrapArguments = "${var.bootstrap_arguments}"
    KeyName = "${var.key_name}"
    NodeImageId = "${var.ami}"
    VpcId = "${var.vpc_id}"
    Subnets = "${var.subnets}"
    NodeGroupName = "${local.stack_name}"
    ClusterControlPlaneSecurityGroup = "${var.cp_sg_id}"
    ClusterName = "${var.cluster_name}"
    NodeAutoScalingGroupMinSize = "${var.min_size}"
    NodeAutoScalingGroupMaxSize = "${var.max_size}"
    NodeInstanceType = "${var.node_instance_type}"
    NodeVolumeSize = "${var.node_volume_size}"
    NodeAutoScalingGroupDesiredCapacity = "${var.node_auto_scaling_group_desired_capacity}"
    AssociatePublicIpAddress = "${var.associate_public_ip_address}"
    ProxySecurityGroup = "${var.proxy_security_group}"

  }


  tags = "${merge(
    map("Region", "${var.region}"),
   map("Environment", "${var.environment}"),
   map("Name", "${local.stack_tag_name}"),
   map("Config", "${var.config_name}"),
   map("GeneratedBy", "terraform"),
   map("Role", "${var.role}"),
   map("kubernetes.io/cluster/${var.cluster_name}", "owned"),
   map("DeploymentTarget", "${var.deployment_target}"),
   "${var.extra_tags}"
  )}"


}
