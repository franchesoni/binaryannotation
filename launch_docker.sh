DATADIR=$1
IPADDRESS=$2
PORT=$3

# raise error if no path is given
if [ -z "$DATADIR" ]
then
    echo "No argument supplied! Please add the path to your folder with images."
    exit 1
fi

# raise error if no port is given
if [ -z "$IPADDRESS" ]
then
    echo "No IP address supplied! Please add the IP address."
    exit 1
fi

# raise error if no port is given
if [ -z "$PORT" ]
then
    echo "No port supplied! Please add the port number."
    exit 1
fi


# Modifier la variable PORT dans le fichier .env
sed -i "s/IPADDRESS=.*/IPADDRESS=$IPADDRESS/" .env
sed -i "s/PORT=.*/PORT=$PORT/" .env
sed -i "s/export const IPAddress = .*/export const IPAddress = '$IPADDRESS'/" /reactcode/src/config.js

sed -i "s/export const IPAddress = 'localhost'/export const IPAddress = '$IPADDRESS'/" frontend/build/static/js/main.0d479df1.js.map
sed -i "s/export const port = '8000'/export const port = '$PORT'/" frontend/build/static/js/main.0d479df1.js.map


docker run -p $PORT:8000 -p 6066:6066 -v $DATADIR:/archive --gpus all --pull always franchesoni/binann:0.1 