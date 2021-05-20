resource "aws_eks_cluster" "cluster" {
  name                      = var.eks_config.cluster_name
  enabled_cluster_log_types = var.eks_config.cluster_enabled_log_types
  role_arn                  = aws_iam_role.eks_service_role.arn
  version                   = var.eks_config.eks_version
  tags = var.global_maps.regional_tags

  vpc_config {
    security_group_ids      = compact([aws_security_group.cluster.id])
    subnet_ids              = concat(var.private_subnets_ids, var.public_subnets_ids)
    endpoint_private_access = var.eks_config.cluster_endpoint_private_access
    endpoint_public_access  = var.eks_config.cluster_endpoint_public_access
    public_access_cidrs     = var.eks_config.cluster_endpoint_public_access_cidrs
  }

  timeouts {
    create = var.eks_config.cluster_create_timeout
    delete = var.eks_config.cluster_delete_timeout
  }

  depends_on = [
    aws_iam_role_policy_attachment.cluster_AmazonEKSClusterPolicy,
    aws_iam_role_policy_attachment.cluster_AmazonEKSServicePolicy,
    aws_iam_role_policy_attachment.cluster_AmazonEKSVPCResourceControllerPolicy,
    aws_cloudwatch_log_group.cluster,
    aws_security_group.cluster,
    aws_security_group_rule.cluster_egress_internet
  ]
}

resource "aws_cloudwatch_log_group" "cluster" {
  count             = length(var.eks_config.cluster_enabled_log_types) > 0 ? 1 : 0
  name              = "/aws/eks/${var.eks_config.cluster_name}/cluster"
  retention_in_days = var.eks_config.cluster_log_retention_in_days
//  tags              = var.eks_config.tags
}

################################
#   EKS IAM
################################

resource "aws_iam_role" "eks_service_role" {
  name               = "${var.eks_config.cluster_name}.eksServiceRole"
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

data "aws_iam_policy" "AmazonEKSClusterPolicy" {
  arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

data "aws_iam_policy" "AmazonEKSServicePolicy" {
  arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
}

data "aws_iam_policy" "AmazonEKSVPCResourceController" {
  arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
}

resource "aws_iam_role_policy_attachment" "cluster_AmazonEKSClusterPolicy" {
  policy_arn = data.aws_iam_policy.AmazonEKSClusterPolicy.arn
  role       = aws_iam_role.eks_service_role.name
}

resource "aws_iam_role_policy_attachment" "cluster_AmazonEKSServicePolicy" {
  policy_arn = data.aws_iam_policy.AmazonEKSServicePolicy.arn
  role       = aws_iam_role.eks_service_role.name
}

resource "aws_iam_role_policy_attachment" "cluster_AmazonEKSVPCResourceControllerPolicy" {
  policy_arn = data.aws_iam_policy.AmazonEKSVPCResourceController.arn
  role       = aws_iam_role.eks_service_role.name
}
################################
#   EKS OIDC
################################

data "tls_certificate" "cluster" {
  url = aws_eks_cluster.cluster.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "cluster" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.cluster.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.cluster.identity[0].oidc[0].issuer
}

data "aws_iam_policy_document" "example_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.cluster.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:kube-system:aws-node"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.cluster.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "example" {
  assume_role_policy = data.aws_iam_policy_document.example_assume_role_policy.json
  name               = "example"
}

################################
#   EKS and Worker Nodes SG
################################

resource "aws_security_group" "cluster" {
  name_prefix = var.eks_config.cluster_name
  description = "EKS cluster control plane security group."
  vpc_id      = var.vpc_id
  tags = {
    "Name" = "${var.eks_config.cluster_name}-eks_cluster_sg"
  }

}

resource "aws_security_group" "nodes" {
  name_prefix = var.eks_config.cluster_name
  description = "Security group for all nodes in the cluster"
  vpc_id = var.vpc_id
  tags = {
    "Name" = "${var.eks_config.cluster_name}-eks_cluster_nodes_sg"
  }
}
################################
#   EKS Control Panel SG Rules
################################

resource "aws_security_group_rule" "cluster_egress_internet" {
  description       = "Allow cluster egress access to the Internet."
  protocol          = "-1"
  security_group_id = aws_security_group.cluster.id
  cidr_blocks       = var.eks_config.cluster_egress_cidrs
  from_port         = 0
  to_port           = 0
  type              = "egress"
}

resource "aws_security_group_rule" "worker_https_to_cluster_ingress" {
  description              = "Allow pods to communicate with the cluster API Server."
  protocol                 = "tcp"
  security_group_id        = aws_security_group.cluster.id
  source_security_group_id = aws_security_group.nodes.id
  from_port                = 443
  to_port                  = 443
  type                     = "ingress"
}

resource "aws_security_group_rule" "cluster_https_to_worker_egress" {
  description              = "Allow the cluster control plane to communicate with pods running extension API servers on port 443."
  protocol                 = "tcp"
  security_group_id        = aws_security_group.nodes.id
  source_security_group_id = aws_security_group.cluster.id
  from_port                = 443
  to_port                  = 443
  type                     = "egress"
}

resource "aws_security_group_rule" "worker_https_cluster_ingress" {
  description              = "Allow pods running extension API servers on port 443 to receive communication from cluster control plane."
  protocol                 = "tcp"
  security_group_id        = aws_security_group.nodes.id
  source_security_group_id = aws_security_group.cluster.id
  from_port                = 443
  to_port                  = 443
  type                     = "ingress"
}

################################
#   K8S Kubelet SG Rules
################################

resource "aws_security_group_rule" "workers_to_workers_ingress" {
  description              = "Allow nodes to communicate with each other."
  protocol                 = "-1"
  security_group_id        = aws_security_group.nodes.id
  source_security_group_id = aws_security_group.nodes.id
  from_port                = 0
  to_port                  = 65535
  type                     = "ingress"
}

resource "aws_security_group_rule" "cluster_to_workers_kubelet_ingress" {
  description              = "Allow worker Kubelets and pods to receive communication from the cluster control plane."
  protocol                 = "tcp"
  security_group_id        = aws_security_group.nodes.id
  source_security_group_id = aws_security_group.cluster.id
  from_port                = 1025
  to_port                  = 65535
  type                     = "ingress"
}

resource "aws_security_group_rule" "workers_to_cluster_kubelet_egress" {
  description              = "Allow the cluster control plane to communicate with worker Kubelet and pods."
  protocol                 = "tcp"
  security_group_id        = aws_security_group.nodes.id
  source_security_group_id = aws_security_group.cluster.id
  from_port                = 1025
  to_port                  = 65535
  type                     = "egress"
}

