print('importing packages in iotofiles.py')
import fcntl
from pathlib import Path
import pickle
import time
from typing import Any

import torch
print('finished importing packages in iotofiles.py')

from config import DEVICE

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
        except (EOFError, pickle.UnpicklingError):
            time.sleep(1)
            print('error reading file, trying again...')

    return ret

def safely_save_torch(net: torch.nn.Module, path: str | Path):
    safely_write(path, net.to('cpu'))

def safely_load_torch(net: torch.nn.Module, path: str | Path) -> torch.nn.Module:
    return safely_read(path).to(DEVICE)
