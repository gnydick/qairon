region = "us-west-2"

environment = "infra"
tier = "public"
config = "default"
role = "dns"
dept = "services"
org = "withMe"
zones = {
  "withme.com": {
    "Tier": "Public"
  },
  "withme.de": {
    "Tier": "Public"
  }
}


subdomains = {
  "withme.com" = {
    "api" = {
      "Tier" = "Public"
    },
    "cicd" = {
      "Tier" = "Public"
    },
    "cm-api" = {
      "Tier" = "Public"
    },
    "cm-dev" = {
      "Tier" = "Public"
    },
    "cm-int-1" = {
      "Tier" = "Public"
    },
    "cm-int-2" = {
      "Tier" = "Public"
    },
    "cm-int-m" = {
      "Tier" = "Public"
    },
    "cm-perf-1" = {
      "Tier" = "Public"
    },
    "content" = {
      "Tier" = "Public"
    },
    "cs-api" = {
      "Tier" = "Public"
    },
    "cs-int-2" = {
      "Tier" = "Public"
    },
    "cs-perf-1" = {
      "Tier" = "Public"
    },
    "dev" = {
      "Tier" = "Public"
    },
    "gs-api" = {
      "Tier" = "Public"
    },
    "gs-int-2-test" = {
      "Tier" = "Public"
    },
    "gs-int-2" = {
      "Tier" = "Public"
    },
    "int-1" = {
      "Tier" = "Public"
    },
    "int-2-portal-int" = {
      "Tier" = "Public"
    },
    "int-2" = {
      "Tier" = "Public"
    },
    "int-m" = {
      "Tier" = "Public"
    },
    "jenkins" = {
      "Tier" = "Public"
    },
    "perf-1" = {
      "Tier" = "Public"
    },
    "portal-int" = {
      "Tier" = "Public"
    },
    "vault" = {
      "Tier" = "Public"
    }
  }

  "withme.de" = {}

}