region = "us-west-2"

requesting-cidr = {
  "ng-prod1" = "10.6.0.0/16",
  "ng-stage1" = "10.5.0.0/16",
  "ng-dev2" = "10.3.0.0/16",
  "leg-dev" = "172.20.0.0/16",
  "leg-dev-new" = "10.100.0.0/16"
}
accepting-vpc_id = "vpc-08ae4961b35a0ca43"
requesting-vpc_id = {
  "ng-prod1" = "vpc-079f4dbb270609bfa",
  "ng-stage1"="vpc-0eb8dda919459679c",
  "ng-dev2" = "vpc-03ee9362c1de18754",
  "leg-dev" = "vpc-0782393378703e19b",
  "leg-dev-new" = "vpc-04c41cf5a4c2b282e"
}
req-sgs = {
  "ng-prod1" = "sg-02bd1bac69fae1c9b",
  "ng-stage1" = "sg-01afde70af5fb8067",
  "ng-dev2" = "sg-0a83a28e09f2c3fb0",
  "leg-dev" = "sg-01268e3fdd22c8781"
  "leg-dev-new" =  "sg-056036a1f7bc16700,sg-0f2e49df341363d6c,sg-0eeb59d44ee545d42,sg-056036a1f7bc16700,sg-039d940a4941388d8,sg-0cdf069aab5d68521,sg-0afe094a8fbe84f7c"

}

config_name = "default"
sg_environment = "dev"
environment = "peering"
deployment_target = "dev_ng1-us-west-2-eks"
requester_account = {
  "ng-stage1" = "115767377948",
  "ng-dev2" = "973104111996",
  "leg-dev" = "973104111996",
  "leg-dev-new" = "966494614521"
}
status = {
  "ng-prod1" = "active",
  "ng-stage1" = "active",
  "ng-dev2" = "active",
  "leg-dev" = "active",
  "leg-dev-new" = "active"
}

allow_dns_in = true