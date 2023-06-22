DATADIR=$1
# raise error if no argument is given
if [ -z "$DATADIR" ]
then
    echo "No argument supplied! Please add the path to your folder with images."
    exit 1
fi

rm -rf docker_results
mkdir docker_results
docker run -p 8000:8000 -p 6066:6066 -v $DATADIR:/archive -v docker_results:/results --gpus all --pull always franchesoni/binann:0.1 