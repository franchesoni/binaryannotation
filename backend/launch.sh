#!/bin/bash
NEWIPADDRESS=$1
NEWPORT=$2
NEWPORTplus1=$((NEWPORT+1))
# add dockermode as third optional argument that defaults to true
DOCKERMODE=${3:-true}
# add datadir as fourth optional argument that defaults to /readonlydir
DATADIR=${4:-/readonlydir}

print_help() {
  echo "Usage: launch.sh NEWIPADDRESS NEWPORT [DOCKERMODE] [DATADIR]"
  echo "  NEWIPADDRESS: the IP address of the machine where the frontend is running"
  echo "  NEWPORT: the port of the machine where the frontend is running"
  echo "  DOCKERMODE: whether to run in dockermode or not (defaults to true)"
  echo "  DATADIR: the path to the folder with images (defaults to /readonlydir)"
  echo -e "Example: launch.sh 127.0.0.1 8077 false /home/user/images\n\n"
  echo "Note that DATADIR is only used in localmode. In dockermode, the images are mounted as a volume."
}

# show help if arguments aren't given
if [ -z "$NEWIPADDRESS" ] || [ -z "$NEWPORT" ]
then
    print_help
    exit 1
fi
# raise error if dockermode is true and datadir isn't default
if [ "$DOCKERMODE" = true ] && [ "$DATADIR" != "/readonlydir" ]
then
    echo "You are running in dockermode, but you supplied a custom datadir. Please use the default datadir."
    exit 1
fi

# print arguments
echo -e "NEWIPADDRESS: $NEWIPADDRESS\nNEWPORT: $NEWPORT\nDOCKERMODE: $DOCKERMODE\nDATADIR: $DATADIR\n"

echo 'started launch!'

reset_placeholders() {
  echo "Resetting placeholders..."
  # reset IP address and port in frontend
  find ../frontend -type f -exec sed -i "s/$(echo ${NEWIPADDRESS} | sed 's/\./\\./g')/IPADDRESSPLACEHOLDER/g" {} +
  find ../frontend -type f -exec sed -i "s/${NEWPORT}/PORTPLACEHOLDER/g" {} +
  # reset IP address and port in config.py file
  sed -i "s/$(echo ${NEWIPADDRESS} | sed 's/\./\\./g')/IPADDRESSPLACEHOLDER/g" config.py
  sed -i "s/${NEWPORT}/PORTPLACEHOLDER/g" config.py
  # reset dockermode in config.py file
  sed -i "s/${DOCKERMODE^}/DOCKERMODEPLACEHOLDER/g" config.py
}

# Define a function to terminate all background processes
term_all_processes() {
  reset_placeholders
  echo "Sending TERM signal to all background jobs..."
  for proc in $(jobs -lp); do # loop over the PIDs of the background jobs
    echo "Stopping PID $proc"
    if kill -0 $proc 2>/dev/null; then # check if the process exists
      kill -TERM $proc # send a terminate signal to the process
    else
      echo "No such process" # print an error message
    fi
  done
  exit 1 # exit the script with an error code
}

# Register a handler to call term_all_processes on ctrl+c
trap term_all_processes INT

# reset
if [ "$DOCKERMODE" = true ]
then
    echo "Running in dockermode"
    rm -rf /iodir/runs/
    rm /iodir/annotations.pickle
    rm /iodir/predictor.ckpt
else
    echo "Running in localmode"
    rm -rf iodir/runs/
    rm iodir/annotations.pickle
    rm iodir/predictor.ckpt
fi
rm predictions.pickle
rm ranking.pickle

# set IP address and port in frontend
find ../frontend -type f -exec sed -i "s/IPADDRESSPLACEHOLDER/$(echo ${NEWIPADDRESS} | sed 's/\./\\./g')/g" {} +
find ../frontend -type f -exec sed -i "s/PORTPLACEHOLDER/${NEWPORT}/g" {} +
# set IP address and port in config.py file
sed -i "s/IPADDRESSPLACEHOLDER/$(echo ${NEWIPADDRESS} | sed 's/\./\\./g')/g" config.py
sed -i "s/PORTPLACEHOLDER/${NEWPORT}/g" config.py
# set dockermode in config.py file considering python true and false start with uppercase
sed -i "s/DOCKERMODEPLACEHOLDER/${DOCKERMODE^}/g" config.py

echo "Starting tensorboard, training, inference and selector scripts..."
# set logdir depending on docker
if [ "$DOCKERMODE" = true ]
then
    LOGDIR=/iodir/runs/
else
    LOGDIR=iodir/runs/
fi

tensorboard --logdir ${LOGDIR} --port ${NEWPORTplus1} --bind_all --reuse_port=true --path_prefix='/tensorboard' &
echo "tensorboard PID: $!"
python -um IA.training &
echo "Script training.py PID: $!"
python -um IA.inference &
echo "Script inference.py PID: $!"
python -um IA.selector &
echo "Script selector.py PID: $!"
python -um backend 

reset_placeholders
wait # wait for the background processes to finish

