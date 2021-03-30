# Migration Paths
root for all new content starts in `nextgen`
```
nextgen
├── docker
│         ├── bin
│         └── defs
├── helm
│         ├── charts
│         └── values
├── jenkins
├── kube
├── ops
├── packer
│         └── defs
│             ├── amazon-eks-ami
│             │         ├── files
│             │         ├── log-collector-script
│             │         │         ├── linux
│             │         │         └── windows
│             │         └── scripts
│             └── fork-example-amazon-eks-ami
│                 ├── files
│                 ├── log-collector-script
│                 │         ├── linux
│                 │         └── windows
│                 └── scripts
├── sceptre
├── terraform
└── tools

```

# Languages
## Python - 3.8.8
3.9.x has some incompatibilities with our code

### pyenv - latest
**Installation**

```curl https://pyenv.run | bash```

**pyenv-virtualenv plugin - latest**

```
git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
```

**Update .bashrc**
```
export PYENV_ROOT=$HOME/.pyenv
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
---
### Using
```
pyenv install 3.8.8
```
Create a new ***venv*** and ***requirements.txt*** for each module
```
pyenv virtualenv 3.8.8 <module>-3.8.8
echo <module>-3.8.8 > <module_base_dir>/.python-version
```

# Tooling
## Installation Types
Tools are installed in one of two ways
### Version Independent
```
${HOME}/tools/<tool_binary>

e.g.
${HOME}/tools/jenkins-cli.jar
```

### Version Specific
```
${HOME}/tools/<tool_binary>/<version>/<tool_binary>

e.g.
${HOME}/tools/kubectl/1.20.2/kubectl
```
## Tools
### direnv
***direnv*** keeps your environment setup to point to the right resources and configurations. We arrange our directories hierarchically in order to represent the hierarchy of configurations.

In order to take advantage of the version of tool you need for any context, update environment

```
# ./us-west-2/.envrc
export PATH=$PATH:${HOME}/tools/kubectl/${KUBE_CLIENT_VERSION}


# ./us-west-2/cluster-foo/.envrc
export KUBE_CLIENT_VERSION=1.20.2
source_env ..
```

This will set your kubectl version when you go into the cluster-foo directory then reevaluate the PATH env var to point to the right binary

### minikube
#### installing multiple versions of k8s
***TBD***

# How To
## aws common cli tasks

Login to the aws ecr taking advantage of our environment driven config

```
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com
```