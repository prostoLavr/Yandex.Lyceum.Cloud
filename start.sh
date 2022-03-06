#!/bin/bash
app="docker.cloud"
docker build -t ${app} .
docker run -d -p 56800:80 \
  --name=${app} \
  -v $PWD:/app ${app}
