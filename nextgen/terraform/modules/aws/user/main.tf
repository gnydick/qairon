resource "aws_iam_user" "user" {
  name = var.user
}

resource "aws_iam_access_key" "access_key" {
  user       = aws_iam_user.user.name
  depends_on = [aws_iam_user.user]
}

output "name" {
  value = aws_iam_user.user.name
}

