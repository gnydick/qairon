data "template_file" "amazon-eks-nodegroup_yaml" {
  template = file("${path.module}/amazon-eks-nodegroup.yaml")

}



resource "aws_cloudformation_stack" "stack" {
  tags = var.global_maps.regional_tags
  name = format("%s-%s", var.global_strings.regional_prefix, var.name)
  capabilities = [
  "CAPABILITY_IAM"]
  template_body = data.template_file.amazon-eks-nodegroup_yaml.rendered


  parameters = {
    BootstrapArguments                  = var.nodegroup_config.bootstrap_arguments
    KeyName                             = var.nodegroup_config.key_name
    NodeImageId                         = var.nodegroup_config.ami
    VpcId                               = var.vpc_id
    Subnets                             = var.subnets
    NodeGroupName                       = var.nodegroup_config.name
    SharedNodeSecurityGroup             = var.shared_node_sg
    ClusterControlPlaneSecurityGroup    = var.cp_sg_id
    ClusterName                         = var.cluster_name
    NodeAutoScalingGroupMinSize         = var.nodegroup_config.min_size
    NodeAutoScalingGroupMaxSize         = var.nodegroup_config.max_size
    NodeInstanceType                    = var.nodegroup_config.node_instance_type
    NodeVolumeSize                      = var.nodegroup_config.node_volume_size
    NodeAutoScalingGroupDesiredCapacity = var.nodegroup_config.node_auto_scaling_group_desired_capacity
    AssociatePublicIpAddress            = var.nodegroup_config.associate_public_ip_address

  }





}
