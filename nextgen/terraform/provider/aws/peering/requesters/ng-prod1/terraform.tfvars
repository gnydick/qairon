accepter-cidr = {
  "ng-dev1" = "10.1.0.0/16"
}

accepter-account = {
  "ng-dev1" = "966494614521"
}
accepter-vpc_id = {
  "ng-dev1" = "vpc-08ae4961b35a0ca43"
}
region = "us-west-2"
requester_cidr = "10.6.0.0/16"
requester_vpc = "prod.us-west-2.1.vpc"
requester_vpc_id = "vpc-079f4dbb270609bfa"


environment = "peering"
accepter-sgs = {
  "ng-dev1" = "sg-00485b73649f1de3a"
}
config_name = "default"

allow_dns_out = true
requester_sgs_tag_name = "ng-prod1-us-west-2-eks.stacks-proxy.sg"
status = {
  "ng-dev1" = "active"
}