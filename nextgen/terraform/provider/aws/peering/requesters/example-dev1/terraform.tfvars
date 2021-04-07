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
requester_cidr = "172.20.0.0/16"
requester_vpc = "dev.foo.k8s.local"
requester_vpc_id = "vpc-0782393378703e19b"


environment = "peering"
accepter-sgs = {
  "example-dev1" = "sg-00485b73649f1de3a"
}
config_name = "default"

allow_dns_out = true
requester_sgs_tag_name = "nodes.dev.foo.k8s.local"
status = {
  "example-dev1" = "active"
}
requester_eks_sgs = ["sg-01268e3fdd22c8781"]
