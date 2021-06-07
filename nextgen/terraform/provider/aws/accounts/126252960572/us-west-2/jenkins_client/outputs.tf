output "secret_arn"{
  value = aws_secretsmanager_secret.jenkins-api-key.arn
}

output "secret_id" {
  value = aws_secretsmanager_secret.jenkins-api-key.id
}
output "kms_key_alias" {
  value = aws_kms_alias.automation-key-alias.name
}

output "kms_key_arn" {
  value = aws_kms_key.automation-key.arn
}

output "kms_key_id" {
  value = aws_kms_key.automation-key.id
}
