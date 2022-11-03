#!/bin/bash

docker build -t dist-fed-core-fl . -f fl/Dockerfile

docker build -t dist-fed-core-identity . -f identity/Dockerfile
docker build -t dist-fed-core-identity-client . -f identity/client/Dockerfile
docker build -t dist-fed-core-identity-issuer . -f identity/issuer/Dockerfile
docker build -t dist-fed-core-identity-verifier . -f identity/verifier/Dockerfile