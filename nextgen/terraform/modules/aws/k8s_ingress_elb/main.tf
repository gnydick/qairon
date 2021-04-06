resource "aws_elb" "k8s-ingress-elb" {
  name = "${var.name}-ing-elb"

  listener = {
    instance_port     = "${var.listener_instance_port}"
    instance_protocol = "${var.listener_instance_protocol}"
    lb_port           = "${var.listener_lb_port}"
    lb_protocol       = "${var.listener_lb_protocol}"
  }

  security_groups = ["${var.lb_sgs}"]
  subnets         = ["${var.ingress_subnet_ids}"]

  health_check = {
    target              = "${var.healthcheck_target}"
    healthy_threshold   = "${var.healthcheck_healthy_threshold}"
    unhealthy_threshold = "${var.healthcheck_unhealthy_threshold}"
    interval            = "${var.healthcheck_interval}"
    timeout             = "${var.healthcheck_timeout}"
  }

  idle_timeout = 300

  tags = "${merge(
   map("Region", "${var.region}"),
   map("Environment", "${var.environment}"),
   map("Name", "${var.name}"),
   map("Config", "${var.config_name}"),
   map("GeneratedBy", "terraform"),
   map("Role", "${var.role}"),
   map("kubernetes.io/cluster/${var.cluster_name}", "owned"),
   map("DeploymentTarget", "${var.deployment_target}"),
   "${var.extra_tags}"
  )}"
}

