module "ark" {
  source = "../../../../../modules/velero"
  region = "${var.region}"
  ark_bucket = "${var.ark_bucket}"
  ark_user = "${var.ark_user}"
}

