resource "aws_lb" "k8s-ingress-nlb" {
  name               = "${var.name}-ing-elb"
  load_balancer_type = "network"

  subnets = var.ingress_subnet_ids

  idle_timeout = 300

  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = var.name
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    {
      "Role" = var.role
    },
    {
      "kubernetes.io/cluster/${var.cluster_name}" = "owned"
    },
    {
      "DeploymentTarget" = var.deployment_target
    },
    var.extra_tags,
  )
}

resource "aws_lb_listener" "ingress-listener" {
  load_balancer_arn = aws_lb.k8s-ingress-nlb.arn
  port              = var.listener_lb_port
  default_action {
    target_group_arn = aws_lb_target_group.ingress-instances.arn
    type             = "forward"
  }
  protocol = var.listener_lb_protocol
}

resource "aws_lb_target_group" "ingress-instances" {
  name        = var.cluster_name
  port        = var.listener_instance_port
  protocol    = "TCP"
  vpc_id      = var.vpc_id
  target_type = "instance"
}

data "aws_instances" "ingress-instances" {
  instance_tags = {
    Role = "ingresssvcs"
  }
}

resource "aws_lb_target_group_attachment" "ingress-instance-attachments" {
  count            = length(data.aws_instances.ingress-instances.ids)
  target_group_arn = aws_lb_target_group.ingress-instances.arn
  target_id        = element(data.aws_instances.ingress-instances.ids, count.index)
}

