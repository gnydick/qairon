# Kiam

Is a tool for pinning AWS IAM Roles to Pods.

## Kiam server

Kiam server runs as an server on "int-2-tire=util" in EKS cluster and resolve STS get credentials requests that comes from "pod->kiam-agent->kiam-server"

[ Kiam v3.4 IAM documentation ](https://github.com/uswitch/kiam/blob/v3.4/docs/IAM.md)

## Kiam agent

Kiam runs as an agent on "int-2-tire=microservice" in EKS cluster and allows cluster users to associate IAM roles to Pods.

## cfssl

"cfssl" is a tool for easy generation of self-signed TLS certificates.
In `cfssl-json` directory you can find json templates used for generating self-signed TLS certificates.
That self-signed TLS certificates used for secured communication between `kiam-server` and `kiam-agent`.

[ Kiam v3.4 TLS documentation ](https://github.com/uswitch/kiam/blob/v3.4/docs/TLS.md)

### Who do I talk to? ###

* mklipikov@imvu.com
