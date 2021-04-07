output "nodegroup_id" {
  value = aws_cloudformation_stack.stack.id
}

output "security_group_id" {
  value = aws_cloudformation_stack.stack.outputs["NodeSecurityGroup"]
}

output "nodegroup_name" {
  value = aws_cloudformation_stack.stack.name
}

