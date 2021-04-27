

resource "aws_security_group_rule" "cluster_https_worker_ingress" {
  description              = "Allow pods to communicate with the EKS cluster API."
  protocol                 = "tcp"
  security_group_id        = var.cluster_security_group_id
  source_security_group_id = aws_security_group_rule.worker_security_group_id.id
  from_port                = 443
  to_port                  = 443
  type                     = "ingress"
}