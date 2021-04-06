data "aws_caller_identity" "core-lib" {}
data "aws_availability_zones" "available" {
  state = "available"
}