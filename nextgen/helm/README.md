# New Chart Changes Needed
* delete `version: ` line from `Chart.yaml`
* remove `values.yaml` from the chart structure and place a copy of it in each deployment target and name it the same name as the chart `values.yaml --> <service_name>.yaml`  
* replace docker image tag value in each of the `values.yaml` files with `%--tag--%`