provider "aws" {
  region = var.region
}

module "vpc" {
  source = "./vpc"
  environment = var.environment
  region = var.region
}

# module "perf-1" {
#   source = "./perf-1"
#   azs = "${var.azs}"
#   config_name = "${var.config_name}"
#   cp_sg_id = "${module.perf-1.control_sg_id}"
#   environment = "${var.environment}"
#   extra_tags = {}
#   private_subnet_ids = "${module.vpc.private_subnet_ids}"
#   public_subnet_ids = "${module.vpc.public_subnet_ids}"
#   region = "${var.region}"
#   vpc_cidr = "${var.vpc_cidr}"
#   vpc_id = "${module.vpc.vpc_id}"

#   private_subnet_cidrs = "${var.private_subnet_cidrs["perf-1"]}"
#   public_subnet_cidrs = "${var.public_subnet_cidrs["perf-1"]}"
# }


# data "template_file" "dev_ecr_access_policy" {
#   template = "${file("./ecr_access.json")}"
# }


//data "template_file" "prod_proxy_can_assume_dev_ecr_access_policy" {
//  template = "${file("./prod_proxy_can_assume_dev_ecr_access_policy.json")}"
//  vars {
//    ecr_access_role = "${aws_iam_role.dev_ecr_only_access_role.name}",
//    dev_ecr_only_access_role_arn = "${aws_iam_role.dev_ecr_only_access_role.arn}"
//  }
//}


//resource "aws_iam_role" "dev_ecr_only_access_role" {
//  name = "prod_access_to_ecr_role"
//  assume_role_policy = <<EOF
//{
//  "Version": "2012-10-17",
//  "Statement": [
//    {
//      "Effect": "Allow",
//      "Principal": {
//        "Service": "eks.amazonaws.com"
//      },
//      "Action": "sts:AssumeRole"
//    }
//  ]
//}
//
//EOF
//}

//resource "aws_iam_role" "proxy_role_for_prod" {
//  assume_role_policy = <<EOF
//{
//  "Version": "2012-10-17",
//  "Statement": [
//    {
//      "Effect": "Allow",
//      "Principal": {
//        "AWS": [
//          "arn:aws:iam::530827097669:role/eksWorkers-prod1-us-west-2-stack1-NodeInstanceRole-XXO35E2ZF3RU",
//          "arn:aws:iam::530827097669:role/eksWorkers-prod1-us-west-2-stack2-NodeInstanceRole-FVTAJOCV2EI5"
//        ]
//      },
//      "Action": "sts:AssumeRole",
//      "Condition": {}
//    }
//  ]
//}
//EOF
//  description = "proxy_role_for_prod"
//  name = "proxy_role_for_prod"
//}


//resource "aws_iam_policy" "dev_ecr_only_access_policy" {
//  policy = "${data.template_file.dev_ecr_access_policy.rendered}"
//}
//
//resource "aws_iam_policy_attachment" "ecr_access_for_prod" {
//
//  name = "ecr_access_for_prod"
//  policy_arn = "${aws_iam_policy.dev_ecr_only_access_policy.arn}"
//  roles = [
//    "${aws_iam_role.proxy_role_for_prod.name}"]
//}
