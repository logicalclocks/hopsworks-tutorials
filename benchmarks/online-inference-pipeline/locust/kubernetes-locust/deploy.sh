#!/bin/bash
kubectl create namespace locust

kubectl apply -f master-deployment.yaml -n locust
kubectl apply -f slave-deployment.yaml -n locust
kubectl apply -f service.yaml -n locust
kubectl apply -f nodeport.yaml -n locust