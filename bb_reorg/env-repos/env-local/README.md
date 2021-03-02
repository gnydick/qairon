# env-local

Provides the automation to start up a local integration test environment.

You will need to have the following installed on your development machine:

* [Docker](https://docs.docker.com/install/)
* [AWS CLI](https://aws.amazon.com/cli/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)

Use [EGO devenv](https://bitbucket.org/imvu/ego-cicd-devenv/src/master/SETUP.md)
to install the above.

Install these manually:

* [VirtualBox](https://drive.google.com/open?id=1758JSOHpq71ubnFx31pzU7jroMruw3DT)

Please note you *must* use the version of VirtualBox in the google drive link
above.  Newer ones might not work.

Also, you will need to have an account on AWS with access to the **Ego Services**.

Use the start-local-env.sh to start up the environment in a local VM:
```
./start-local-env.sh [manifest1.yaml manifest2.yaml, etc]
```
This will start an HTML page that has links to some handle tools:
* Kubernetes Dashboard
* NGiNX+ Dashboard
* Log Files for Ego Services

Note that after running the above script, your Docker configuration is using the daemon running
inside the minikube VM (rather than your local machine).  You can use the same shell to run
Docker commands to add images built locally that you want to test.

Undeploy the Ego Services:
```
./stop-local-env.sh
```

Redeploy the Ego Servers (presumably after making a change):
```
./start-local-env.sh
```

Re-run the script that produces the HTML page (from the root of the env-local repo)
```
./gen-index-html.sh local-basic.yaml > out/index.html
```

Deploy logging services:
```
./start-logging-services.sh
```

Undeploy logging services:
```
./stop-logging-services.sh
```

Shutdown the cluster:
```
minikube stop
```

After the minikube stop, you can remove the VM to start later from a clean slate (when necessary):
```
minikube delete
```