#!/bin/bash
# Set variables
IMAGE_NAME=binann
IMAGE_TAG=0.1
REGISTRY_URL=franchesoni

# Build image
docker image build -t $IMAGE_NAME:$IMAGE_TAG .

DATADIR=$1
NEWIPADDRESS=$2
NEWPORT=$3
NEWPORTplus1=$((NEWPORT+1))
# raise error if no argument is given
if [ -z "$DATADIR" ]
then
    echo "No argument supplied! Please add the path to your folder with images."
    exit 1
fi
if [ -z "$NEWIPADDRESS" ]
then
    echo "No NEWIPADDRESS supplied! Please add the new IP address so we can configure the frontend."
    exit 1
fi
if [ -z "$NEWPORT" ]
then
    echo "No NEWPORT supplied! Please add the new port so we can configure the frontend."
    exit 1
fi

rm -rf docker_results
mkdir docker_results
# docker run -p $NEWPORT:8077 -p $NEWPORTplus1:8078 --mount type=bind,source=$DATADIR,target=/readonlydir,readonly --mount source=docker_results,target=/iodir --gpus all --pull always franchesoni/binann:0.1 $NEWIPADDRESS $NEWPORT
docker run -p $NEWPORT:8077 -p $NEWPORTplus1:8078 --mount type=bind,source=$DATADIR,target=/readonlydir,readonly --mount source=docker_results,target=/iodir -it $IMAGE_NAME:$IMAGE_TAG $NEWIPADDRESS $NEWPORT