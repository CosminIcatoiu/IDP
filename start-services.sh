#!/bin/bash

#Start the service as a deamon
docker-compose run -d --name tema_service_run_1 service

#Get the ip of the service in the created network
ip_s=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' tema_service_run_1)

#Start the clientdocker-compose run -T -e ip_service=$ip_s client


