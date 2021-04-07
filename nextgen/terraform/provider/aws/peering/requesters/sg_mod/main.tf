resource "aws_security_group_rule" "old-dev-to-eks-443" {
  count = var.status == "active" ? length(var.accepter-sgs) * length(var.requester_eks_sgs) : 0
  security_group_id = element(
    var.requester_eks_sgs,
    count.index / length(var.accepter-sgs),
  )
  from_port                = 443
  protocol                 = "tcp"
  source_security_group_id = element(var.accepter-sgs, count.index)
  to_port                  = 443
  type                     = "ingress"
}

resource "aws_security_group_rule" "old-dev-to-80" {
  count                    = var.status == "active" ? length(var.accepter-sgs) * length(var.requester_sgs) : 0
  security_group_id        = element(var.requester_sgs, count.index / length(var.accepter-sgs))
  from_port                = 80
  protocol                 = "tcp"
  source_security_group_id = element(var.accepter-sgs, count.index)
  to_port                  = 80
  type                     = "egress"
}

resource "aws_security_group_rule" "old-dev-to-443" {
  count                    = var.status == "active" ? length(var.accepter-sgs) * length(var.requester_sgs) : 0
  security_group_id        = element(var.requester_sgs, count.index / length(var.accepter-sgs))
  from_port                = 443
  protocol                 = "tcp"
  source_security_group_id = element(var.accepter-sgs, count.index)
  to_port                  = 443
  type                     = "egress"
}

resource "aws_security_group_rule" "old-dev-from-80" {
  count                    = var.status == "active" ? length(var.accepter-sgs) * length(var.requester_sgs) : 0
  security_group_id        = element(var.requester_sgs, count.index / length(var.accepter-sgs))
  from_port                = 80
  protocol                 = "tcp"
  source_security_group_id = element(var.accepter-sgs, count.index)
  to_port                  = 80
  type                     = "ingress"
}

resource "aws_security_group_rule" "old-dev-from-443" {
  count                    = var.status == "active" ? length(var.accepter-sgs) * length(var.requester_sgs) : 0
  security_group_id        = element(var.requester_sgs, count.index / length(var.accepter-sgs))
  from_port                = 443
  protocol                 = "tcp"
  source_security_group_id = element(var.accepter-sgs, count.index)
  to_port                  = 443
  type                     = "ingress"
}

