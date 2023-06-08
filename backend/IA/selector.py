from pathlib import Path

import numpy as np
from IA.iotofiles import safely_read, safely_write

from config import predspath, rankingpath

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
                predictions = safely_read(predspath)
                ranking = selector(predictions)
                safely_write(ranking, rankingpath)
                last_modified = modified_at
                    


if __name__ == "__main__":
    selector = max_prob_selector
    continuously_rank(selector=selector)

