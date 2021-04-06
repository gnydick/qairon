
resource "aws_ecr_repository" "aws_docker_repo" {
  count = "${length(var.repos)}"
  name = "${element(var.repos, count.index)}"

  image_scanning_configuration {
    scan_on_push = element(var.scan_on_push, count.index)
  }
}