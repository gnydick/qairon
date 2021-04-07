accepter-cidr = {
  "example-dev1" = "10.1.0.0/16"
}

accepter-account = {
  "example-dev1" = "966494614521"
}
accepter-vpc_id = {
  "example-dev1" = "vpc-08ae4961b35a0ca43"
}
region = "us-west-2"
requester_cidr = "10.3.0.0/16"
requester_vpc = "dev.us-west-2.1.vpc"
requester_vpc_id = "vpc-03ee9362c1de18754"


environment = "peering"
accepter-sgs = {
  "example-dev1" = "sg-00485b73649f1de3a"
}
config_name = "default"

allow_dns_out = true
requester_sgs_tag_name = "example-dev2-us-west-2-eks.stacks-proxy.sg"
status = {
  "example-dev1" = "pending-acceptance"
}