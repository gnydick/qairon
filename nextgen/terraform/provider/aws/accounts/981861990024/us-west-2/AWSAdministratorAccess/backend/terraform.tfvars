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
config = "default"
org = "withme"
region = "us-west-2"
dept = "services"

#dynamodb_table
stream_enabled = true
stream_view_type = "NEW_AND_OLD_IMAGES"
billing_mode = "PAY_PER_REQUEST"
role = "tfstate"
