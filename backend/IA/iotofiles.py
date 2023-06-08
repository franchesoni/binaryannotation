import fcntl
import pickle

def safely_write(file, data):
    with open(file, 'wb') as f:
        # Apply an exclusive lock on the file descriptor
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        # Write the data using pickle
        pickle.dump(data, f)
        # Release the lock on the file descriptor
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def safely_read(file):
    with open(file, 'rb') as f:
        # Apply a shared lock on the file descriptor
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        # Read the data using pickle
        ret = pickle.load(f)  # {index: probability}
        # Release the lock on the file descriptor
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return ret
