# Generating the TLS/SSL Secrets in the local.yaml

The local.yaml file has a couple of secrets supporting TLS.  Here is how I created them:

```
kubectl create secret tls tls-certificate --key service-gateway.key --cert service-gateway.pem 
kubectl create secret generic tls-dhparam --from-file=dhparam.pem 
kubectl get secrets
kubectl get secret tls-dhparam -o yaml
kubectl get secret tls-certificate -o yaml
```

The service-gateway.key and service-gateway.pem files are copied from the service-gateway repo:

```
service-gateway/local/cert-tools/server
```

The dhparam.pem was created using this command inside that same directory:

```
openssl dhparam -out dhparam.pem 2048
```

