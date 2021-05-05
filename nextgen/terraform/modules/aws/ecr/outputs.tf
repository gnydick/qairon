output "this_ecr_repository_name" {
  description = "The name of the repository"
  value       = aws_ecr_repository.this.name
}

output "this_ecr_repository_arn" {
  description = "Full ARN of the repository"
  value       = aws_ecr_repository.this.arn
}

output "this_ecr_repository_registry_id" {
  description = "The registry ID where the repository was created"
  value       = aws_ecr_repository.this.registry_id
}

output "this_ecr_repository_repository_url" {
  description = "The URL of the repository (in the form aws_account_id.dkr.ecr.region.amazonaws.com/repositoryName"
  value       = aws_ecr_repository.this.repository_url
}

