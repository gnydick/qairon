resource "tls_private_key" "private_key" {
  algorithm = "${var.algorithm}"

  lifecycle {
    create_before_destroy = true
  }

}
