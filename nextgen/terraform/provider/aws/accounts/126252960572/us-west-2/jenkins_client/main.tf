module "jenkins-client" {
  source = "../../../../../../modules/aws/sa-iam-role"
  cluster_oidc_provider = data.terraform_remote_state.vpc.outputs.cluster_oidc_providers["vpc0"]["infra0"]
  cluster_oidc_provider_arn = data.terraform_remote_state.vpc.outputs.cluster_oidc_provider_arns["vpc0"]["infra0"]
  role_name = "JenkinsAutomationClient"
  sa = "system:serviceaccount:default:jenkins-automation-client"
}





resource "aws_secretsmanager_secret" "jenkins-api-key" {
  name = format("%s-jenkins-api-key.secret", local.global_strings.regional_prefix)
  kms_key_id = aws_kms_key.automation-key.id
}

resource "aws_kms_key" "automation-key" {
  description = "key to decrypt automation secrets"
  enable_key_rotation = true
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
}

resource "aws_kms_alias" "automation-key-alias" {

  target_key_id = aws_kms_key.automation-key.id
  name = "alias/jenkins-infra-vpc0-infra0"
}

resource "aws_iam_policy" "jenkins-automation-client-policy" {
  name = "JenkinsAutomationClientPolicy"
  policy =<<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "kms:Decrypt",
        "kms:DescribeKey"
      ],
      "Effect": "Allow",
      "Resource": "${aws_kms_key.automation-key.arn}"
    },
    {
      "Action": [
        "secretsmanager:DescribeSecret",
        "secretsmanager:GetSecretValue"
      ],
      "Effect": "Allow",
      "Resource": "${aws_secretsmanager_secret.jenkins-api-key.arn}"
    }
  ]
}


EOF
}

resource "aws_iam_role_policy_attachment" "jenkins-secret-api-key" {

  policy_arn = aws_iam_policy.jenkins-automation-client-policy.arn
  role = module.jenkins-client.role_name
}