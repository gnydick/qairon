provider "aws" {
  region = "${var.region}"
}

resource "aws_ses_configuration_set" "dev1_ses_config" {
  name = "${var.cluster}"
}

resource "aws_ses_domain_identity" "dev1_ses_identity" {
  domain = "${var.domain}"
}

resource "aws_ses_domain_mail_from" "dev1_ses_mail_from" {
  domain = "${aws_ses_domain_identity.dev1_ses_identity.domain}"
  mail_from_domain = ""
}

resource "aws_ses"
