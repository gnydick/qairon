org = "withme"
dept = "services"
environment = "infra"
role = "automation"
config = "default"
region = "us-west-2"
provider_region = "us-west-2"

repos = [
  "jenkins",
  "qairon",
  "ghost-proxy",
  "helm",
  "aws",
  "docker"
]

repo_prefix= "arn:aws:ecr:us-west-2:126252960572:repository"

ro_principal_identifiers = [
 "arn:aws:iam::417738154227:root", #"int":
  "arn:aws:iam::702861675511:root", # "dev"
  "arn:aws:iam::923799771136:root" #"prod"
]
