* `modules`: modules for reuse
* `provider`: base of hydrated configs, dir per cloud provider

#Notes
## `modules`
* no hardcoded values

## `provider`
* variable values defined at top level in `terraform.tfvars`, not in `variables.tf` files
* try to avoid overrides

## General
* use `terraform_remote_state` to store and lookup values between unrelated modules, for example, needing a `vpc_id` from the `vpc` implemented module
