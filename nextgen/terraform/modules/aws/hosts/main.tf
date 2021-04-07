data "template_file" "start_docker_and_rancher" {
  template = file("${path.module}/${var.rancher_service_template}")
  vars = {
    token       = var.token
    checksum    = var.checksum
    kube_role   = var.kube_role
    region      = var.aws_region
    rancher_url = var.rancher_url
  }
}

locals {
  common_tags = {
    Region           = var.aws_region
    Environment      = var.environment
    Config           = var.config_name
    GeneratedBy      = "terraform"
    Role             = var.role
    InstanceType     = var.instance_type
    DeploymentTarget = var.deployment_target
  }
}

resource "aws_instance" "server" {
  count                       = var.host_count
  iam_instance_profile        = var.iam_instance_profile
  instance_type               = var.instance_type
  ami                         = element(var.amis, count.index)
  key_name                    = var.key_name
  subnet_id                   = element(var.subnet_ids, count.index)
  vpc_security_group_ids      = var.security_groups
  associate_public_ip_address = var.associate_public_ip_address
  availability_zone           = element(var.azs, count.index)
  user_data                   = data.template_file.start_docker_and_rancher.rendered

  tags = merge(
    local.common_tags,
    var.custom_tags,
    {
      "Name" = "${count.index}.${var.environment}.${var.region}"
      "AZ"   = element(var.azs, count.index)
    },
  )
}

resource "aws_route53_record" "private_ip" {
  count   = length(aws_instance.server)
  name    = count.index
  type    = "A"
  ttl     = "10"
  zone_id = var.zone_id
  records = [
    element(aws_instance.server.*.private_ip, count.index),
  ]
}

resource "aws_ebs_volume" "docker_volume" {
  count             = var.host_docker_vol_count
  size              = var.docker_image_vol_size
  type              = "gp2"
  availability_zone = element(var.azs, count.index)

  tags = merge(
    "Region",
    var.region,
    "Environment",
    var.environment,
    "Name",
    "${count.index}.${var.environment}.${var.region}.docker_volume",
    "Config",
    var.config_name,
    "GeneratedBy",
    "terraform",
    "AZ",
    element(var.azs, count.index),
    "Role",
    var.role,
    "kubernetes.io/cluster/prod1-us-west-2",
    "owned",
  )
}

resource "aws_volume_attachment" "docker_volume_attachment" {
  count = var.host_docker_vol_count

  device_name  = var.docker_image_device_name
  instance_id  = element(aws_instance.server.*.id, count.index)
  volume_id    = element(aws_ebs_volume.docker_volume.*.id, count.index)
  force_detach = true
}

