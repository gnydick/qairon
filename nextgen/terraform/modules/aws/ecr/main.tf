
resource "aws_ecr_repository" "aws_docker_repo" {
  for_each = var.repos
  name     = each.value
  image_scanning_configuration {
    scan_on_push = true
  }

}