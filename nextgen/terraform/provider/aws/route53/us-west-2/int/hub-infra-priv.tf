resource "aws_route53_zone" "hub-infra" {
  force_destroy = "false"

  name = "hub.infra.priv"
  vpc {
    vpc_id = "vpc-08ae4961b35a0ca43"
    vpc_region = "${var.region}"
  }
  vpc {
    vpc_id = "vpc-0fdfd77cda33f681c"
    vpc_region = "${var.region}"
  }

  vpc {
    vpc_id = "vpc-0eb8dda919459679c"
    vpc_region = "${var.region}"
  }
  vpc {
    vpc_id = "vpc-0782393378703e19b"
    vpc_region = "${var.region}"
  }



  vpc {
    vpc_id = "vpc-079f4dbb270609bfa"
    vpc_region = "${var.region}"
  }

  vpc {
    vpc_id = "vpc-03ee9362c1de18754"
    vpc_region = "${var.region}"
  }
}


resource "aws_route53_record" "fooa-hub-lb" {
  name = "fooa"
  type = "CNAME"
  zone_id = "${aws_route53_zone.hub-infra.zone_id}"
  records = [
    "${data.aws_elb.fooa-lb.dns_name}"]
  ttl = 10
}


resource "aws_route53_record" "metrics-hub-lb" {
  name = "metrics"
  type = "CNAME"
  zone_id = "${aws_route53_zone.hub-infra.zone_id}"
  records = [
    "${data.aws_elb.metrics-lb.dns_name}"]
  ttl = 10
}

resource "aws_route53_record" "jenkins-hub-lb" {
  name = "jenkins"
  type = "CNAME"
  zone_id = "${aws_route53_zone.hub-infra.zone_id}"
  records = [
    "${data.aws_elb.jenkins-hub-infra-priv-lb.dns_name}"]
  ttl = 10
}

resource "aws_route53_record" "jenkins-hub-agentlb" {
  name = "jenkins-agent"
  type = "CNAME"
  zone_id = "${aws_route53_zone.hub-infra.zone_id}"
  records = [
    "${data.aws_elb.jenkins-agent-lb.dns_name}"]
  ttl = 10
}