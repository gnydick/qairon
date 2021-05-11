region = "us-west-2"

environment = "infra"
tier = "public"
config = "default"
role = "dns"
dept = "services"
org = "withMe"
zones = ["withme.com", "withme.de"]


subdomains = {
  "withme.de" = [],
  "withme.com" = [
    "alertmanager-ui.withme.com",
    "api.withme.com",
    "cicd.withme.com",
    "cm-api.withme.com",
    "cm-dev.withme.com",
    "cm-int-1.withme.com",
    "cm-int-2.withme.com",
    "cm-int-m.withme.com",
    "cm-perf-1.withme.com",
    "content.withme.com",
    "cs-api.withme.com",
    "cs-int-2.withme.com",
    "cs-perf-1.withme.com",
    "dev.withme.com",
    "grafana-cicd.withme.com",
    "grafana-int-2.withme.com",
    "grafana-perf-1.withme.com",
    "grafana-ui.withme.com",
    "gs-api.withme.com",
    "gs-int-2-test.withme.com",
    "gs-int-2.withme.com",
    "int-1.withme.com",
    "int-2-portal-int.withme.com",
    "int-2.withme.com",
    "int-m.withme.com",
    "jaeger-elb.withme.com",
    "jaeger-ui.withme.com",
    "jaegercollector.withme.com",
    "jenkins.withme.com",
    "kibana-elb.withme.com",
    "kibana-ui.withme.com",
    "perf-1.withme.com",
    "portal-int.withme.com",
    "vault.withme.com"
  ]

}