import fcntl
from pathlib import Path
import pickle

import tqdm
import numpy as np

from config import ckptpath, annfilepath, datadir, predspath, rankingpath
from IA.training import Predictor
from IA.dataset import FullDataset, UnlabeledDataset

def random_selector(predictions):
    predlist = list(predictions.items())
    np.random.shuffle(predlist)
    return predlist

def max_entropy_selector(predictions):
    probs = np.array(predictions.values())
    scores = np.abs(probs - 0.5)  # smaller is better
    indices = np.argsort(scores)  # smaller first
    predlist = np.array(predictions.items())
    predlist = predlist[indices]
    return predlist

def min_entropy_selector(predictions):
    probs = np.array(predictions.values())
    scores = -np.abs(probs - 0.5)  # smaller is better
    indices = np.argsort(scores)  # smaller first
    predlist = np.array(predictions.items())
    predlist = predlist[indices]
    return predlist

def min_prob_selector(predictions):
    probs = np.array(predictions.values())
    indices = np.argsort(probs)  # smaller first
    predlist = np.array(predictions.items())
    predlist = predlist[indices]
    return predlist

def max_prob_selector(predictions):
    probs = np.array(predictions.values())
    indices = np.argsort(-probs)  # smaller first
    predlist = np.array(predictions.items())
    predlist = predlist[indices]
    return predlist


def continuously_rank(selector, predspath=predspath):
    last_modified = 0
    while True:
        if Path(predspath).is_file():
            modified_at = Path(predspath).stat().st_mtime
            if last_modified < modified_at:
                with open(predspath, 'rb') as f:
                    # Apply a shared lock on the file descriptor
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    # Read the data using pickle
                    predictions = pickle.load(f)  # {index: probability}
                    # Release the lock on the file descriptor
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                predlist = selector(predictions)
                with open(predspath, 'wb') as f:
                    # Apply an exclusive lock on the file descriptor
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    # Write the data using pickle
                    pickle.dump(predlist, f)
                    # Release the lock on the file descriptor
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

                last_modified = modified_at
                    


if __name__ == "__main__":
    selector = max_prob_selector
    continuously_rank(selector=selector)

