locals {
  cluster_iam_role_name = join("", aws_iam_role.eks_service_role.*.name)
  cluster_iam_role_arn = join("", aws_iam_role.eks_service_role.*.arn)
  cluster_short_name = var.name
  cluster_long_name = "${var.global_strings.regional_prefix}-${var.name}"

}

