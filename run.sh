#!/bin/bash
docker build -t=app:0.0.1 .
docker run --rm -v $PWD:/app -p 8080:8080 app:0.0.1
