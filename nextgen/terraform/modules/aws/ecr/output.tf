output "repos" {
  value = tomap({
  for r, repo in aws_ecr_repository.aws_docker_repo: r => repo
  })
}