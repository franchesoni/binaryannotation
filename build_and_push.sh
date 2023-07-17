#!/bin/bash
# Build and push docker image script

# Set variables
IMAGE_NAME=binann
IMAGE_TAG=0.1
REGISTRY_URL=franchesoni

# Build image
docker image build -t $IMAGE_NAME:$IMAGE_TAG .
# make sure to tag the image with the registry url
docker image tag $IMAGE_NAME:$IMAGE_TAG $REGISTRY_URL/$IMAGE_NAME:$IMAGE_TAG

# Push image
docker image push $REGISTRY_URL/$IMAGE_NAME:$IMAGE_TAG
