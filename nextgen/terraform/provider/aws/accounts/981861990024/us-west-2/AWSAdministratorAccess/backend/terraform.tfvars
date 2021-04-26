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
environment = "sandbox"
config_tag = "default"
org = "withme"
region = "us-west-2"
role = "infra"

#dynamodb_table
stream_enabled = false
stream_view_type = ""
billing_mode = "PAY_PER_REQUEST"
tflock_dynamodb_table_name = "tfstate"
tflock_dynamodb_hash_key = "LockID"
tflock_dynamodb_hash_key_type = "S"
tflock_dynamodb_write_capacity = 0
