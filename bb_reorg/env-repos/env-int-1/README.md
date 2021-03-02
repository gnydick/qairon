# env-int-1

This repository provides the automation to startup and shutdown the int-1 Integration Testing Environment
in the AWS cloud provider by Jenkins Pipeline.

## Prerequisites

Access to Jenkins Dashboard. If you will need full Pipeline build log.

## Jenkins Pipeline Usage
There are two Jenkins Pipeline Scripts "Jenkinsfile-int-1-auto-integration-test" and "Jenkinsfile-int1-tear-down"
First, one is to build a full "int-1" environment and deploys all needed there and run integration test.
This Pipeline can take 20-23 minutes to run to completion, so you can kick it off and go do something else for a
while and just check your build status in Slack channel __#jenkins_notifications__.

If build runs successfully, the latest tested service docker image tag will be changed to new in his k8s manifest.
A Jenkins Pipeline can be kick-started manually from the Jenkins Dashboard and automatically from Bitbucket Pipeline.
Job have two parameters for build:
*  Parameters :
     * APP_NAME (as example 'game-state-manager')
     * APP_VERSION (as example '1.0.0')

The second Pipeline is for cleanup he deletes all things that the first one created.
That pipeline will be always triggered after the first one (SUCCESS/FAILED) for keeping clean our AWS Account.
This Pipeline can take 15-19 minutes.

If you want to know how exactly Jenkins Pipeline work and where you can find some logs from "int-1" environment, check [Confluence Page](https://confluence.corp.imvu.com/display/EGO/Automatic+Integration+Tests+Design#AutomaticIntegrationTestsDesign-JenkinsPipeline).

__NOTE: These two Jenkins Pipelines are not allowed concurrent builds so all new builds will be in a queue.__
