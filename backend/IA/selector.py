from pathlib import Path

import numpy as np

from IA.iotofiles import safely_read, safely_write
from config import predspath, rankingpath

np.random.seed(0)

def random_selector(predictions: dict):
    predlist = list(predictions.items())  # (index, prob)
    np.random.shuffle(predlist)
    return predlist

def max_entropy_selector(predictions):
    probs = np.array(list(predictions.values()))
    scores = np.abs(probs - 0.5)  # smaller is better
    indices = np.argsort(scores)  # smaller first
    predlist = np.array(list(predictions.items()))
    predlist = predlist[indices]
    return predlist

def min_entropy_selector(predictions):
    predlist = np.array(list(predictions.items()))
    probs = np.array([p[1] for p in predlist])
    valid_probs = probs[probs >= 0]
    scores = -np.abs(valid_probs - 0.5)  # smaller is better
    indices = np.argsort(scores)  # smaller first
    predlist = np.concatenate((predlist[probs >=0][indices], predlist[probs < 0]), axis=0)
    return predlist

def min_prob_selector(predictions):
    predlist = np.array(list(predictions.items()))
    probs = np.array([p[1] for p in predlist])
    valid_probs = probs[probs >= 0]
    scores = valid_probs  # smaller is better
    indices = np.argsort(scores)  # smaller first
    predlist = np.concatenate((predlist[probs >=0][indices], predlist[probs < 0]), axis=0)
    return predlist

def max_prob_selector(predictions: dict):
    predlist = np.array(list(predictions.items()))
    probs = np.array([p[1] for p in predlist])
    indices = np.argsort(-probs)  # smaller first
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
                safely_write(rankingpath, ranking)
                print(">>> ranking updated")
                last_modified = modified_at
                    

def init_ranking(state, rankingpath=rankingpath):
    # create ranking
    indices = np.array(state.dataset.to_annotate_indices)
    probs = np.ones_like(indices) * 0.5
    ranking = np.concatenate([indices[:, None], probs[:, None]], axis=1)
    safely_write(rankingpath, ranking)




if __name__ == "__main__":
    selector = max_prob_selector
    continuously_rank(selector=selector)

