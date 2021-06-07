data "aws_iam_policy_document" "sa-assume-role-policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${var.cluster_oidc_provider}:sub"
      values   = [var.sa]
    }

    principals {
      identifiers = [var.cluster_oidc_provider_arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "sa" {
  assume_role_policy = data.aws_iam_policy_document.sa-assume-role-policy.json
  name               = var.role_name
  lifecycle {
    create_before_destroy = false
  }
}

