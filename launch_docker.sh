DATADIR=$1
# docker run -p 8000:8000 -p 6066:6066 -v $DATADIR:/archive --pull always franchesoni/binann:0.1 
docker run -p 8000:8000 -p 6066:6066 -v $DATADIR:/archive --gpus all --pull always franchesoni/binann:0.1 