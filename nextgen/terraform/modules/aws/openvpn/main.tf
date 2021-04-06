#--------------------------------------------------------------
# This module creates all resources necessary for OpenVPN
#--------------------------------------------------------------


resource "aws_security_group" "openvpn" {
  config_name = "${var.config_name}"
  vpc_id      = "${var.vpc_id}"
  description = "OpenVPN security group"

  tags {
    Region = "${var.region}"
    Environment = "${var.environment}"
    Name        = "${var.environment}.${var.region}.openvpn.sg"
    Config      = "${var.config_name}"
    GeneratedBy = "terraform"
    DeploymentTarget = "${var.deployment_target}"
    "kubernetes.io/cluster/prod1-us-west-2"     = "owned"
  }

  ingress {
    protocol    = -1
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["${var.vpc_cidr}"]
  }

  # For OpenVPN Client Web Server & Admin Web UI
  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol    = "udp"
    from_port   = 1194
    to_port     = 1194
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = -1
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "openvpn" {
  ami           = "${var.ami}"
  instance_type = "${var.instance_type}"

  //  key_name   = "${var.key_name}"
  subnet_id = "${element(var.public_subnet_ids, count.index)}"

  vpc_security_group_ids = ["${aws_security_group.openvpn.id}"]

  tags {
    Region = "${var.region}"
    Environment = "${var.environment}"
    Name        = "${var.environment}.${var.region}.openvpn"
    Config      = "${var.config_name}"
    GeneratedBy = "terraform"
    DeploymentTarget = "${var.deployment_target}"
    "kubernetes.io/cluster/prod1-us-west-2"     = "owned"
  }

  # `admin_user` and `admin_pw` need to be passed in to the appliance through `user_data`, see docs -->
  # https://docs.openvpn.net/how-to-tutorialsguides/virtual-platforms/amazon-ec2-appliance-ami-quick-start-guide/
  user_data = <<USERDATA
admin_user=${var.openvpn_admin_user}
admin_pw=${var.openvpn_admin_pw}
USERDATA

  provisioner "remote-exec" {
    connection {
      user         = "${var.openvpn_user}"
      host         = "${self.private_ip}"
      private_key  = "${var.private_key}"
      bastion_host = "${var.bastion_host}"
      bastion_user = "${var.bastion_user}"
    }

    inline = [
      # Insert our SSL cert
      "echo '${var.ssl_cert}' | sudo tee /usr/local/openvpn_as/etc/web-ssl/server.crt > /dev/null",

      "echo '${var.ssl_key}' | sudo tee /usr/local/openvpn_as/etc/web-ssl/server.key > /dev/null",

      # Set VPN network info
      "sudo /usr/local/openvpn_as/scripts/sacli -k vpn.daemon.0.client.network -v ${element(split("/", var.vpn_cidr), 0)} ConfigPut",

      "sudo /usr/local/openvpn_as/scripts/sacli -k vpn.daemon.0.client.netmask_bits -v ${element(split("/", var.vpn_cidr), 1)} ConfigPut",

      # Do a warm restart so the config is picked up
      "sudo /usr/local/openvpn_as/scripts/sacli start",
    ]
  }
}

variable "azs" {}
variable "environment" {}
variable "region" {}

resource "aws_route53_record" "openvpn" {
  count   = "${length(var.azs)}"
  zone_id = "${var.route_zone_id}"
  name    = "${var.environment}.${var.region}.${element(var.azs, count.index)}.vpn"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.openvpn.public_ip}"]
}

output "private_ip" {
  value = "${aws_instance.openvpn.private_ip}"
}

output "public_ip" {
  value = "${aws_instance.openvpn.public_ip}"
}

output "public_fqdn" {
  value = "${aws_route53_record.openvpn.fqdn}"
}
