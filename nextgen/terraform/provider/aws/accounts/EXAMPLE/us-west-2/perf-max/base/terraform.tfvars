#--------------------------------------------------------------
# General
#--------------------------------------------------------------

# When using the GitHub integration, variables are not updated
# when checked into the repository, only when you update them
# via the web interface. When making variable changes, you should
# still check them into GitHub, but don't forget to update them
# in the web UI of the appropriate environment as well.

# If you change the atlas_environment name, be sure this name
# change is reflected when doing `terraform remote config` and
# `terraform push` commands - changing this WILL affect your
# terraform.tfstate file, so use caution
environment = "perf-1"
config_name = "default"

region = "us-west-2"

#--------------------------------------------------------------
# Network
#--------------------------------------------------------------

vpc_cidr = "10.6.0.0/16"

vpc_add_cidr = {

}

azs = [
  "us-west-2a",
  "us-west-2b",
  "us-west-2c"] # AZs are region specific

private_subnet_cidrs = {
  perf-1 = [
    "10.6.0.0/20",
    "10.6.16.0/20",
    "10.6.32.0/20",
  ],

  perf-1-rds = [
    "10.6.48.0/24",
    "10.6.49.0/24",
    "10.6.50.0/24",
  ],

  resolver = [
    "10.6.51.0/30",
    "10.6.51.4/30",
    "10.6.51.8/30"]

}

public_subnet_cidrs = {
  perf-1 = [
    "10.6.51.0/28",
    "10.6.51.16/28",
    "10.6.51.32/28",
  ],

  reserved = [
    "10.6.224.0/20",
    "10.6.240.0/20",
  ],

}

//  clusters = [
//    "perf-1",
//    ]



backend_bucket = ""
statefile_name = ""
locking_dsn = ""
