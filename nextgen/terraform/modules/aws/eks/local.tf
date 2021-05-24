locals {
  cluster_iam_role_name = join("", aws_iam_role.eks_service_role.*.name)
  cluster_iam_role_arn  = join("", aws_iam_role.eks_service_role.*.arn)
}