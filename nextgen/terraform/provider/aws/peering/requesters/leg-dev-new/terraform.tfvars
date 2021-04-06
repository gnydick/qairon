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
requester_cidr = "10.100.0.0/16"
requester_vpc = "Foo"
requester_vpc_id = "vpc-04c41cf5a4c2b282e"


environment = "peering"
accepter-sgs = {
  "ng-dev1" = "sg-00485b73649f1de3a"
}
config_name = "default"

allow_dns_out = true
requester_sgs_tag_name = "Foo"
status = {
  "ng-dev1" = "active"
}
requester_eks_sgs = ["sg-056036a1f7bc16700","sg-0f2e49df341363d6c","sg-0eeb59d44ee545d42","sg-056036a1f7bc16700","sg-039d940a4941388d8","sg-0cdf069aab5d68521","sg-0afe094a8fbe84f7c",""]
