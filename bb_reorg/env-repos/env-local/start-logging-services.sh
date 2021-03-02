#!/bin/bash

echo "Setup rbac for fluentd"
kubectl apply -f fluentd-rbac.yml

echo "Deploy ElasticSearch service"
kubectl apply -f elastic.yml

echo "Deploy Fluentd daemon service"
kubectl apply -f fluentd-elasticsearch.yml

echo "Deploy Kibana service"
kubectl apply -f kibana.yml

echo "Deploy Jaeger service"
kubectl apply -f jaeger.yml

