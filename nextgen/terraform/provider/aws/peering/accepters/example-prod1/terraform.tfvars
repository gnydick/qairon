region = "us-west-2"

requesting-cidr = {
  "example-prod1" = "10.6.0.0/16",
  "example-stage1" = "10.5.0.0/16",
  "example-dev2" = "10.3.0.0/16",
  "example-dev1" = "172.20.0.0/16",
  "example-dev1-new" = "10.100.0.0/16"
}
accepting-vpc_id = "vpc-08ae4961b35a0ca43"
requesting-vpc_id = {
  "example-prod1" = "vpc-079f4dbb270609bfa",
  "example-stage1"="vpc-0eb8dda919459679c",
  "example-dev2" = "vpc-03ee9362c1de18754",
  "example-dev1" = "vpc-0782393378703e19b",
  "example-dev1-new" = "vpc-04c41cf5a4c2b282e"
}
req-sgs = {
  "example-prod1" = "sg-02bd1bac69fae1c9b",
  "example-stage1" = "sg-01afde70af5fb8067",
  "example-dev2" = "sg-0a83a28e09f2c3fb0",
  "example-dev1" = "sg-01268e3fdd22c8781"
  "example-dev1-new" =  "sg-056036a1f7bc16700,sg-0f2e49df341363d6c,sg-0eeb59d44ee545d42,sg-056036a1f7bc16700,sg-039d940a4941388d8,sg-0cdf069aab5d68521,sg-0afe094a8fbe84f7c"

}

config_name = "default"
sg_environment = "dev"
environment = "peering"
deployment_target = "dev_ng1-us-west-2-eks"
requester_account = {
  "example-stage1" = "115767377948",
  "example-dev2" = "973104111996",
  "example-dev1" = "973104111996",
  "example-dev1-new" = "966494614521"
}
status = {
  "example-prod1" = "active",
  "example-stage1" = "active",
  "example-dev2" = "active",
  "example-dev1" = "active",
  "example-dev1-new" = "active"
}

allow_dns_in = true