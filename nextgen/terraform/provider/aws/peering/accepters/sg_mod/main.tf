resource "aws_security_group_rule" "requester-to-80" {
  count = "${var.status=="active"?length(var.req-sgs)*length(data.aws_security_groups.proxy-sg.ids):0}"
  security_group_id = "${element(data.aws_security_groups.proxy-sg.ids,count.index / length(var.req-sgs)) }"
  from_port = 80
  protocol = "tcp"
  source_security_group_id = "${element(var.req-sgs, count.index)}"
  to_port = 80
  type = "ingress"
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_security_group_rule" "requester-to-443" {
  count = "${var.status=="active"?length(var.req-sgs)*length(data.aws_security_groups.proxy-sg.ids):0}"
  security_group_id = "${element(data.aws_security_groups.proxy-sg.ids,count.index / length(var.req-sgs)) }"
  from_port = 443
  protocol = "tcp"
  source_security_group_id = "${element(var.req-sgs, count.index)}"
  to_port = 443
  type = "ingress"
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_security_group_rule" "requester-from-80" {
  count = "${var.status=="active"?length(var.req-sgs)*length(data.aws_security_groups.proxy-sg.ids):0}"
  security_group_id = "${element(data.aws_security_groups.proxy-sg.ids,count.index / length(var.req-sgs)) }"
  from_port = 80
  protocol = "tcp"
  source_security_group_id = "${element(var.req-sgs, count.index)}"
  to_port = 80
  type = "egress"
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_security_group_rule" "requester-from-443" {
  count = "${var.status=="active"?length(var.req-sgs)*length(data.aws_security_groups.proxy-sg.ids):0}"
  security_group_id = "${element(data.aws_security_groups.proxy-sg.ids,count.index / length(var.req-sgs)) }"
  from_port = 443
  protocol = "tcp"
  source_security_group_id = "${element(var.req-sgs, count.index)}"
  to_port = 443
  type = "egress"
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_security_group_rule" "requester-to-50000" {
  count = "${var.status=="active"?length(var.req-sgs)*length(data.aws_security_groups.proxy-sg.ids):0}"
  security_group_id = "${element(data.aws_security_groups.proxy-sg.ids,count.index / length(var.req-sgs)) }"
  from_port = 443
  protocol = "tcp"
  source_security_group_id = "${element(var.req-sgs, count.index)}"
  to_port = 443
  type = "ingress"
  lifecycle {
    prevent_destroy = true
  }
}
