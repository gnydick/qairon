resource "aws_iam_policy" "policy" {
  name   = "${var.name}-policy"
  policy = var.policy
}

output "arn" {
  value = aws_iam_policy.policy.arn
}

