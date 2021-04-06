resource "aws_route53_zone" "infra-ng" {
  name = "infra.ng.priv"

  lifecycle {
    ignore_changes = ["vpc"]
  }

  vpc {
    vpc_id = "vpc-08ae4961b35a0ca43"
  }
  vpc {
    vpc_id = "vpc-0fdfd77cda33f681c"
  }

  vpc {
    vpc_id = "vpc-0eb8dda919459679c"
  }
  vpc {
    vpc_id = "vpc-0782393378703e19b"
  }

  vpc {
    vpc_id = "vpc-010902e03b38b0f54"
  }

  vpc {
    vpc_id = "vpc-079f4dbb270609bfa"
  }
}


resource "aws_route53_record" "fooa-lb" {
  name = "fooa"
  type = "CNAME"
  zone_id = "${aws_route53_zone.infra-ng.zone_id}"
  records = [
    "${data.aws_elb.fooa-lb.dns_name}"]
  ttl = 10
}


resource "aws_route53_record" "metrics-lb" {
  name = "metrics"
  type = "CNAME"
  zone_id = "${aws_route53_zone.infra-ng.zone_id}"
  records = [
    "${data.aws_elb.metrics-lb.dns_name}"]
  ttl = 10
}

resource "aws_route53_record" "jenkins-lb" {
  name = "jenkins"
  type = "CNAME"
  zone_id = "${aws_route53_zone.infra-ng.zone_id}"
  records = [
    "${data.aws_elb.jenkins-infra-ng-priv-lb.dns_name}"]
  ttl = 10
}

resource "aws_route53_record" "jenkins-agentlb" {
  name = "jenkins-agent"
  type = "CNAME"
  zone_id = "${aws_route53_zone.infra-ng.zone_id}"
  records = [
    "${data.aws_elb.jenkins-agent-lb.dns_name}"]
  ttl = 10
}