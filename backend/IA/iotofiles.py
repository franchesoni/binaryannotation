print('importing packages in iotofiles.py')
import fcntl
from pathlib import Path
import pickle
import time
from typing import Any

import torch
print('finished importing packages in iotofiles.py')

def safely_write(file: str | Path, data: Any):
    with open(file, 'wb') as f:
        # Apply an exclusive lock on the file descriptor
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        # Write the data using pickle
        pickle.dump(data, f)
        # Release the lock on the file descriptor
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def safely_read(file: str | Path) -> Any:
    while True:
        try:
            with open(file, 'rb') as f:
                # Apply a shared lock on the file descriptor
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                # Read the data using pickle
                ret = pickle.load(f)  # {index: probability}
                # Release the lock on the file descriptor
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            break
        except EOFError:
            time.sleep(1)
            print('error reading file, trying again...')

    return ret

def safely_save_torch(net: torch.nn.Module, path: str | Path):
    torch.save(net.state_dict(), path)

def safely_load_torch(net: torch.nn.Module, path: str | Path) -> torch.nn.Module:
    while True:
        try:
            net.load_state_dict(torch.load(path))
            break
        except (EOFError, RuntimeError):
            print('error loading model, trying again...')
            time.sleep(0.1)
    return net
