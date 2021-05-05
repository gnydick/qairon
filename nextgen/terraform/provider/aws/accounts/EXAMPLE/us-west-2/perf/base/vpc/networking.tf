module "networking" {
  source = "../../../../../../../../modules/aws/networking-single-az-gws"

  vpc_id = "${module.vpc.vpc_id}"
  region = "${var.region}"
  config_name = "${var.config_name}"
  public_subnet_cidrs = ["${var.public_subnet_cidrs}"]
  private_subnet_cidrs = ["${var.private_subnet_cidrs}"]
  azs = ["${var.azs}"]
  environment = "${var.environment}"
  extra_tags = {public = {"NgDev1Peer" = "true"}, private = {"NgDev1Peer" = "true"}}
  kube_extra_tags = {
    public = {
      "kubernetes.io/cluster/perf-1-us-west-2-eks" = "shared"
      "kubernetes.io/role/elb" = ""

    },
    private = {
      "kubernetes.io/cluster/perf-1-us-west-2-eks" = "shared"
      "kubernetes.io/role/internal-elb" = ""

    }
  }
}


