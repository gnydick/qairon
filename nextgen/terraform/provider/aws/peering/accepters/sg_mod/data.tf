data "aws_security_groups" "proxy-sg" {
  tags = {
    Environment = var.environment
    Region      = var.region
    GeneratedBy = "terraform"
    Role        = "proxy"
  }
}

