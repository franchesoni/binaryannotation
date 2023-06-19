#!/bin/bash

# build frontend
rm -rf frontend
cd reactcode
npm install
npm run build
mv build ../frontend
cd ..


# Set variables
IMAGE_NAME=binann
IMAGE_TAG=0.1
REGISTRY_URL=franchesoni

# Build image
docker image build -t $IMAGE_NAME:$IMAGE_TAG .

# Launch
docker run -p 8000:8000 -p 6066:6066 -v /home/franchesoni/bastien/archive:/archive binann:0.1 