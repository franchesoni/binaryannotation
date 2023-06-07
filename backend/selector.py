import random
from abc import ABC, abstractmethod

import tqdm
import torch

from torch.utils.data import DataLoader

from predictor import Predictor


class AbstractSelector(ABC):
    @abstractmethod
    def get_next_img(self, state):
        pass

class RandomSelector:
    def __init__(self, seed=0):
        random.seed(seed)

    def get_next_img(self, state):
        return random.sample(list(state.to_annotate_indices), 1)[0]

class MinProbSelector:
    def __init__(self, state):
        self.predictor = Predictor('oracular_0.pt')
        if not hasattr(self, 'ranking'):
            batch_size = 64
            dl = DataLoader(state.dataset, batch_size=batch_size, shuffle=True)
            predictions = []  #torch.empty(len(state.dataset))
            indices = []
            print('Generating scores...')
            for i, (imgind, img, label) in tqdm.tqdm(enumerate(dl), total=len(dl)):
                predictions.append(torch.sigmoid(self.predictor(img))[:, 1].tolist())
                indices.append(imgind.tolist())
                if i == 2:
                    break
            indices = torch.tensor([e for l in indices for e in l])
            self.probs = torch.tensor([e for l in predictions for e in l])
            argsorted_probs = torch.argsort(self.probs)
            self.probs = self.probs[argsorted_probs]
            self.ranking = indices[argsorted_probs]


    def get_next_img(self, state):
        to_annotate_indices = torch.tensor(list(state.to_annotate_indices))
        avail_indices = torch.where(torch.isin(self.ranking, to_annotate_indices))[0]
        return int(self.ranking[avail_indices][0]), self.probs[avail_indices][0]

        



