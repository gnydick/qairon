environment = "prod"
config = "sandbox"
org = "withme"
region = "us-west-2"
provider_region = "us-west-2"
dept = "engineering"

#dynamodb_table
stream_enabled   = true
stream_view_type = "NEW_AND_OLD_IMAGES"
billing_mode     = "PAY_PER_REQUEST"
role             = "tfstate"
