locals {

  cluster_security_group_id = var.cluster_create_security_group ? join("", aws_security_group.cluster.*.id) : var.cluster_security_group_id
  cluster_iam_role_name             = join("", aws_iam_role.eks_service_role.*.name)
}