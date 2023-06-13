DATADIR=$1
# docker run -p 8000:8000 -$DATADIRIR:/archive --gpus all --pull always franchesonbinannnn:0.1 
docker run -p 8000:8000 -v $DATADIR:/archive --pull always franchesoni/binann:0.1 