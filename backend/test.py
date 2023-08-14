import subprocess
import time
import os
import signal

# Run the launch script and capture its output
launch_process = subprocess.Popen ( ["bash", "launch.sh", "localhost", "8077", "false", "../archive/kagglecatsanddogs_3367a/", "true", "try1/", "true"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

# Wait for a few seconds for the server to start
time.sleep(5)

# Run the simulate script
from simulate_ui import TestUI
test = TestUI()
test.setup_method(None)
test.test_firsttrial()
# Wait for the simulate script to finish
test.teardown_method(None)


# Kill the launch script by sending a SIGINT signal to its process group
os.killpg (os.getpgid (launch_process.pid), signal.SIGINT)

# Get the output of the launch script
launch_output, launch_error = launch_process.communicate ()

# Decode the output from bytes to string
launch_output = launch_output.decode ('utf-8')

# Print the output of the launch script
print ("Output of launch.sh:")
print (launch_output)

# # Compare the output against something
# # You can write your own logic here
# # For example, check if the output contains a certain word
# if "success" in launch_output:
#     print ("The launch script was successful")
# else:
#     print ("The launch script failed")
