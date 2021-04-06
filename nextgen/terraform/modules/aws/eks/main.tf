module "sg" {
  source = "security_groups"
  config_name = "${var.config_name}"
  environment = "${var.environment}"
  vpc_id = "${var.vpc_id}"
  region = "${var.region}"

  deployment_target = "${var.deployment_target}"
}

resource "aws_eks_cluster" "cluster" {
  name     = "${var.cluster_name}"
  role_arn = "${aws_iam_role.eks_service_role.arn}"
  version = "${var.eks_version}"
  lifecycle {
    ignore_changes = ["enabled_cluster_log_types"]
  }
  enabled_cluster_log_types = ["api","audit","authenticator","controllerManager","scheduler"]


  vpc_config {
    subnet_ids  = ["${concat(var.private_subnet_ids, var.public_subnet_ids)}"]
    security_group_ids = ["${module.sg.cp_sg_id}"]
    endpoint_private_access = true
  }
}

output "endpoint" {
  value = "${aws_eks_cluster.cluster.endpoint}"
}

output "kubeconfig-certificate-authority-data" {
  value = "${aws_eks_cluster.cluster.certificate_authority.0.data}"
}



resource "aws_iam_role" "eks_service_role" {

  name = "${var.cluster_name}.eksServiceRole"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

EOF

}
data "aws_iam_policy" "AmazonEKSServicePolicy" {
  arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
}


data "aws_iam_policy" "AmazonEKSClusterPolicy" {
  arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}


resource "aws_iam_role_policy_attachment" "eks_clstr_attch" {
  policy_arn = "${data.aws_iam_policy.AmazonEKSClusterPolicy.arn}"
  role = "${aws_iam_role.eks_service_role.name}"
}

resource "aws_iam_role_policy_attachment" "eks_svc_attch" {
  policy_arn = "${data.aws_iam_policy.AmazonEKSServicePolicy.arn}"
  role = "${aws_iam_role.eks_service_role.name}"
}
