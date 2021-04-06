variable "role" {
  default = "opentsdb"
}
resource "aws_iam_policy" "opentsdb_emr_policy" {
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Resource": "*",
            "Action": [
                "ec2:AuthorizeSecurityGroupEgress",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:CancelSpotInstanceRequests",
                "ec2:CreateNetworkInterface",
                "ec2:CreateSecurityGroup",
                "ec2:CreateTags",
                "ec2:DeleteNetworkInterface",
                "ec2:DeleteSecurityGroup",
                "ec2:DeleteTags",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeAccountAttributes",
                "ec2:DescribeDhcpOptions",
                "ec2:DescribeImages",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeInstances",
                "ec2:DescribeKeyPairs",
                "ec2:DescribeNetworkAcls",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribePrefixLists",
                "ec2:DescribeRouteTables",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSpotInstanceRequests",
                "ec2:DescribeSpotPriceHistory",
                "ec2:DescribeSubnets",
                "ec2:DescribeTags",
                "ec2:DescribeVpcAttribute",
                "ec2:DescribeVpcEndpoints",
                "ec2:DescribeVpcEndpointServices",
                "ec2:DescribeVpcs",
                "ec2:DetachNetworkInterface",
                "ec2:ModifyImageAttribute",
                "ec2:ModifyInstanceAttribute",
                "ec2:RequestSpotInstances",
                "ec2:RevokeSecurityGroupEgress",
                "ec2:RunInstances",
                "ec2:TerminateInstances",
                "ec2:DeleteVolume",
                "ec2:DescribeVolumeStatus",
                "ec2:DescribeVolumes",
                "ec2:DetachVolume",
                "iam:GetRole",
                "iam:GetRolePolicy",
                "iam:ListInstanceProfiles",
                "iam:ListRolePolicies",
                "iam:PassRole",
                "s3:CreateBucket",
                "s3:Get*",
                "s3:List*",
                "sdb:BatchPutAttributes",
                "sdb:Select",
                "sqs:CreateQueue",
                "sqs:Delete*",
                "sqs:GetQueue*",
                "sqs:PurgeQueue",
                "sqs:ReceiveMessage",
                "cloudwatch:PutMetricAlarm",
                "cloudwatch:DescribeAlarms",
                "cloudwatch:DeleteAlarms",
                "application-autoscaling:RegisterScalableTarget",
                "application-autoscaling:DeregisterScalableTarget",
                "application-autoscaling:PutScalingPolicy",
                "application-autoscaling:DeleteScalingPolicy",
                "application-autoscaling:Describe*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "iam:CreateServiceLinkedRole",
            "Resource": "arn:aws:iam::*:role/aws-service-role/spot.amazonaws.com/AWSServiceRoleForEC2Spot*",
            "Condition": {
                "StringLike": {
                    "iam:AWSServiceName": "spot.amazonaws.com"
                }
            }
        }
    ]
}
EOF
}

resource "aws_iam_policy" "opentsdb_emr_ec2_policy" {
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Resource": "*",
        "Action": [
            "cloudwatch:*",
            "dynamodb:*",
            "ec2:Describe*",
            "elasticmapreduce:Describe*",
            "elasticmapreduce:ListBootstrapActions",
            "elasticmapreduce:ListClusters",
            "elasticmapreduce:ListInstanceGroups",
            "elasticmapreduce:ListInstances",
            "elasticmapreduce:ListSteps",
            "kinesis:CreateStream",
            "kinesis:DeleteStream",
            "kinesis:DescribeStream",
            "kinesis:GetRecords",
            "kinesis:GetShardIterator",
            "kinesis:MergeShards",
            "kinesis:PutRecord",
            "kinesis:SplitShard",
            "rds:Describe*",
            "s3:*",
            "sdb:*",
            "sns:*",
            "sqs:*",
            "glue:CreateDatabase",
            "glue:UpdateDatabase",
            "glue:DeleteDatabase",
            "glue:GetDatabase",
            "glue:GetDatabases",
            "glue:CreateTable",
            "glue:UpdateTable",
            "glue:DeleteTable",
            "glue:GetTable",
            "glue:GetTables",
            "glue:GetTableVersions",
            "glue:CreatePartition",
            "glue:BatchCreatePartition",
            "glue:UpdatePartition",
            "glue:DeletePartition",
            "glue:BatchDeletePartition",
            "glue:GetPartition",
            "glue:GetPartitions",
            "glue:BatchGetPartition",
            "glue:CreateUserDefinedFunction",
            "glue:UpdateUserDefinedFunction",
            "glue:DeleteUserDefinedFunction",
            "glue:GetUserDefinedFunction",
            "glue:GetUserDefinedFunctions"
        ]
    }]
}


EOF
}

resource "aws_iam_role" "opentsdb_emr_role" {
  name = "${var.environment}.${var.region}.opentsdb_emr_role"
  assume_role_policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "elasticmapreduce.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}


resource "aws_iam_role" "opentsdb_emr_ec2_role" {
  name = "${var.environment}.${var.region}.opentsdb_emr_ec2_role"
  assume_role_policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "emr_attachment" {
  roles = ["${aws_iam_role.opentsdb_emr_role.name}"]
  name = "${aws_iam_role.opentsdb_emr_role.name}"
  policy_arn = "${aws_iam_policy.opentsdb_emr_policy.arn}"
}

resource "aws_iam_policy_attachment" "emr_ec2_attachment" {
  roles = ["${aws_iam_role.opentsdb_emr_ec2_role.name}"]
  name = "${aws_iam_role.opentsdb_emr_ec2_role.name}"
  policy_arn = "${aws_iam_policy.opentsdb_emr_ec2_policy.arn}"
}

resource "aws_iam_instance_profile" "emr_instance_profile" {
  name = "${aws_iam_role.opentsdb_emr_ec2_role.name}.profile"
  role = "${aws_iam_role.opentsdb_emr_ec2_role.name}"
}


resource "aws_emr_cluster" "opentsdb" {
  name = "${var.environment}.${var.region}.opentsdb"
  release_label = "${var.emr_version}"
  service_role = "${aws_iam_role.opentsdb_emr_role.name}"
  termination_protection = "${var.termination_protection}"
  applications = [
    "HBase", "Hadoop", "Hue", "Hive", "Pig"
    ]

  instance_group {
    instance_role = "CORE"
    instance_type = "${var.core_instance_type}"
    instance_count = "${var.emr_core_count}"

    ebs_config {
      size = "${var.ebs_core_size}"
      type = "${var.ebs_core_type}"
      volumes_per_instance = "${var.volumes_per_core_instance}"
    }
  }

  instance_group {
    instance_role = "MASTER"
    instance_type = "${var.core_instance_type}"
    instance_count = "1"
    ebs_config {
      size = "${var.ebs_master_size}"
      type = "${var.ebs_master_type}"
      volumes_per_instance = "${var.volumes_per_core_instance}"
    }
  }


  ec2_attributes {
    subnet_id = "${var.subnet_id}"
    instance_profile = "${aws_iam_instance_profile.emr_instance_profile.name}"
    key_name = "${var.key_name}"
    emr_managed_master_security_group = "${aws_security_group.emr_master.id}"
    emr_managed_slave_security_group = "${aws_security_group.emr_slave.id}"
    service_access_security_group = "${aws_security_group.service_access_security_group.id}"

  }
  //"m4.xlarge"

  ebs_root_volume_size = "${var.root_ebs_size}"
  log_uri = "s3://aws-logs-${var.account_no}-${var.region}/elasticmapreduce/"


}



resource "aws_security_group" "emr_master" {
  name        = "${var.environment}.${var.region}.emr_master.sg"
  vpc_id      = "${var.vpc_id}"

  tags {
    Region = "${var.region}"
    Environment = "${var.environment}"
    Name        = "${var.environment}.${var.region}.emr_master.sg"
    Config      = "${var.config_name}"
    GeneratedBy = "terraform"
  }
}

resource "aws_security_group" "emr_slave" {
  name        = "${var.environment}.${var.region}.emr_slave.sg"
  vpc_id      = "${var.vpc_id}"

  tags {
    Region = "${var.region}"
    Environment = "${var.environment}"
    Name        = "${var.environment}.${var.region}.emr_slave.sg"
    Config      = "${var.config_name}"
    GeneratedBy = "terraform"
  }
}

resource "aws_security_group" "service_access_security_group" {
  name        = "${var.environment}.${var.region}.service_access_security_group.sg"
  vpc_id      = "${var.vpc_id}"

  tags {
    Region = "${var.region}"
    Environment = "${var.environment}"
    Name        = "${var.environment}.${var.region}.service_access_security_group.sg"
    Config      = "${var.config_name}"
    GeneratedBy = "terraform"
  }
}