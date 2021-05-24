resource "aws_security_group" "proxy_sg" {
  name = var.name

  description = "proxy for cloudformation stacks so a stack can be deleted without having to break the sg links to other resources"
  vpc_id      = var.vpc_id
  tags = {
    "Name" = var.name
  }


}

resource "aws_security_group_rule" "same_group_egress" {
  //  lifecycle {
  //    prevent_destroy = true
  //  }
  source_security_group_id = aws_security_group.proxy_sg.id
  description              = "hosts allowed to reach each other"

  from_port         = 0
  protocol          = "all"
  security_group_id = aws_security_group.proxy_sg.id
  to_port           = 0
  type              = "egress"
  depends_on = [
  aws_security_group.proxy_sg]
}


resource "aws_security_group_rule" "same_group_ingress" {
  //  lifecycle {
  //    prevent_destroy = true
  //  }
  source_security_group_id = aws_security_group.proxy_sg.id
  description              = "hosts allowed to reach each other"

  from_port         = 0
  protocol          = "all"
  security_group_id = aws_security_group.proxy_sg.id
  to_port           = 0
  type              = "ingress"
  depends_on = [
  aws_security_group.proxy_sg]
}
