#!/bin/bash

echo "Remove rbac for fluentd"
kubectl delete -f fluentd-rbac.yml

echo "Remove ElasticSearch service"
kubectl delete -f elastic.yml

echo "Remove Fluentd daemon service"
kubectl delete -f fluentd-elasticsearch.yml

echo "Remove Kibana service"
kubectl delete -f kibana.yml

echo "Remove Jaeger service"
kubectl delete -f jaeger.yml
