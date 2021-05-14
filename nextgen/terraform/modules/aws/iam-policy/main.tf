data "aws_iam_policy_document" "policy_document" {
  statement {
    sid       = var.iam_policy_document_sid
    effect    = var.iam_policy_document_effect
    actions   = var.iam_policy_document_actions
    resources = var.iam_policy_document_resource_arn
  }
}

resource "aws_iam_policy" "policy" {
  name        = var.name
  path        = var.path
  description = var.description

  policy = data.aws_iam_policy_document.policy_document.json

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "attach_to_role" {
  role       = var.iam_role_name
  policy_arn = aws_iam_policy.policy.arn
}