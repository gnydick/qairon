# Istio

Here you can find k8s manifests for install Istio CRD and deploy Istio Control Plane.

* Install Istio to kubernetes cluster
    1. Shure that you are using "int-2" context.:
       ```
       $ kubectl config current-context
       ```
    2. Shure that you are in the right directory.  `/$path/$to/$repo/env-int-2/istio`:
       ```
       $ pwd
       ```
    3. Create kubernetes namespace for the istio-system components.:
       ```
       $ kubectl create namespace istio-system
       ```
    4. Install Istio CRD as first:
       ```
       $ kubectl apply -f ./istio-init --recursive
       ```
    5. Verify that all 53 Istio CRDs were committed to the Kubernetes api-server using the following command:
       ```
       $ kubectl get crds | grep 'istio.io\|certmanager.k8s.io' | wc -l
       ```
    6. Install Istio Control Plane components:
       ```
       $ kubectl apply -f ./istio-cp --recursive
       ```
    7. Wait and verify that all Istio Control Plane components are "Running" or "Completed".:
       ```
       $ kubectl get pod -n istio-system
       ```

## "istio-manifests" directory

In that directory we store Istio manifests for configuring Istio intelligent routing.
Two main type of Istio networking resource definitions is "Gateway" and "VirtualService".
Checking "VirtualService" and "Gateway" that applied to cluster by kubectl command:
```bash
$ kubectl get gateways.networking.istio.io -n default
NAME           AGE
grpc-gateway   9d
rest-gateway   9d
```
```bash
$ kubectl get virtualservices.networking.istio.io -n default
NAME                      GATEWAYS         HOSTS                        AGE
grafana-rest              [rest-gateway]   [grafana-int-2.withme.com]   4m
kiali-rest                [rest-gateway]   [kiali-int-2.withme.com]     4m
service-gateway-cs-rest   [rest-gateway]   [cs-int-2.withme.com]        9d
service-gateway-grpc      [grpc-gateway]   [cm-int-2.withme.com]        9d
service-gateway-rest      [rest-gateway]   [int-2.withme.com]           9d
```
**Note: Remember that "virtualservices" and "gateways" are namespaced objects and VS that referred to Gateway must be in the same namespace as that Gateway. But VS can route to k8s Services in different namespaces.**

Istio "ServiceEntry" enables adding additional entries into Istio’s internal service registry, so that auto-discovered services in the mesh can access/route to these manually specified services.
We use it to allow service mesh pods (with Envoy Sidecar) communicate with services outside service mesh.
Checking "ServiceEntry" that applied to cluster by kubectl command:
```bash
$ kubectl get serviceentries.networking.istio.io -n default
NAME           HOSTS                                                       LOCATION        RESOLUTION   AGE
int-2-cs-rds   [idbzr1ubk0l4mv.cy4gdlimhn5o.us-west-2.rds.amazonaws.com]   MESH_EXTERNAL   NONE         1h
```
