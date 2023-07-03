#!/bin/bash
echo 'started launch!'
# Define a function to terminate all background processes
term_all_processes() {
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
rm -rf runs/
rm annotations.pickle
rm predictor.ckpt
rm predictions.pickle
rm ranking.pickle

sed -i "s/IPADDRESS = '[^']*'/IPADDRESS = '0.0.0.0'/g" config.py
sed -i "s/PORT = '[^']*'/PORT = '8077'/g" config.py

tensorboard --logdir runs/ --port 8078 --bind_all --reuse_port=true --path_prefix='/tensorboard' &
echo "tensorboard PID: $!"
python -um IA.training &
echo "Script training.py PID: $!"
python -um IA.inference &
echo "Script inference.py PID: $!"
python -um IA.selector &
echo "Script selector.py PID: $!"
python -um backend 

wait # wait for the background processes to finish

