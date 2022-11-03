#!/bin/bash

docker build -t dist-fed-core-fl . -f fl/Dockerfile
docker tag dist-fed-core-fl hmaid/hyperledger:dist-fed-core-fl
docker push hmaid/hyperledger:dist-fed-core-fl

docker build -t dist-fed-core-identity . -f identity/Dockerfile
docker tag dist-fed-core-identity hmaid/hyperledger:dist-fed-core-identity
docker push hmaid/hyperledger:dist-fed-core-identity

docker build -t dist-fed-core-identity-client . -f identity/client/Dockerfile
docker tag dist-fed-core-identity-client hmaid/hyperledger:dist-fed-core-identity-client
docker push hmaid/hyperledger:dist-fed-core-identity-client

docker build -t dist-fed-core-identity-issuer . -f identity/issuer/Dockerfile
docker tag dist-fed-core-identity-issuer hmaid/hyperledger:dist-fed-core-identity-issuer
docker push hmaid/hyperledger:dist-fed-core-identity-issuer

docker build -t dist-fed-core-identity-verifier . -f identity/verifier/Dockerfile
docker tag dist-fed-core-identity-verifier hmaid/hyperledger:dist-fed-core-identity-verifier
docker push hmaid/hyperledger:dist-fed-core-identity-verifier
