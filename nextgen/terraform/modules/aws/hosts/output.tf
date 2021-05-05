output "associate_public_ip_address" {
  value = var.associate_public_ip_address
}

output "instance_ids" {
  value = [aws_instance.server.*.id]
}

output "private_ips" {
  value = [aws_instance.server.*.private_ip]
}

