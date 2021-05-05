resource "aws_security_group_rule" "a_b_in" {
  description              = "${var.nodegroup_a_name}-${var.nodegroup_b_name}-ingress"
  source_security_group_id = var.nodegroup_a_id
  from_port                = 0
  protocol                 = "all"
  security_group_id        = var.nodegroup_b_id
  to_port                  = 0
  type                     = "ingress"
}

resource "aws_security_group_rule" "b_a_in" {
  description              = "${var.nodegroup_b_name}-${var.nodegroup_a_name}-ingress"
  source_security_group_id = var.nodegroup_b_id
  from_port                = 0
  protocol                 = "all"
  security_group_id        = var.nodegroup_a_id
  to_port                  = 0
  type                     = "ingress"
}

resource "aws_security_group_rule" "a_b_out" {
  description              = "${var.nodegroup_a_name}-${var.nodegroup_b_name}-egress"
  source_security_group_id = var.nodegroup_b_id
  from_port                = 0
  protocol                 = "all"
  security_group_id        = var.nodegroup_a_id
  to_port                  = 0
  type                     = "egress"
}

resource "aws_security_group_rule" "b_a_out" {
  description              = "${var.nodegroup_b_name}-${var.nodegroup_a_name}-egress"
  source_security_group_id = var.nodegroup_a_id
  from_port                = 0
  protocol                 = "all"
  security_group_id        = var.nodegroup_b_id
  to_port                  = 0
  type                     = "egress"
}

