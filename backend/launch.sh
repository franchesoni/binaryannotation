#!/bin/bash
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
rm annotations.pickle
rm predictor.ckpt
rm predictions.pickle
rm ranking.pickle


#!/bin/bash
python -m IA.training &
echo "Script training.py PID: $!"
python -m IA.inference &
echo "Script inference.py PID: $!"
python -m IA.selector &
echo "Script selector.py PID: $!"
python -m backend 
# echo "Script backend.py PID: $!"

wait # wait for the background processes to finish

