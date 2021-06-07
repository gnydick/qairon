module "helm-bucket" {
  source = "../../../../../../modules/aws/s3_bucket"
  s3_acl = "private"
  bucket_prefix = "helm-repo-126252960572"
  tags = local.global_tags
}


resource "aws_s3_bucket_object" "helm-stable" {
  bucket = module.helm-bucket.bucket_name
  key = "stable/"
  source = "/dev/null"
  acl = "private"
}

