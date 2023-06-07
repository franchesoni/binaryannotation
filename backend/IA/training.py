from pathlib import Path

import tqdm
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights
import torch
from torch.utils.data import DataLoader

from IA.dataset import FullDataset, LabeledDataset, UnabeledDataset
from config import datadir, ckptpath, annfilepath



class Predictor(torch.nn.Module):  
    def __init__(self, load_from=None):
        super().__init__()
        weights = None if Path(load_from).is_file() else MobileNet_V3_Small_Weights
        self.net = self.get_network(weights=weights)
        if Path(load_from).is_file():
            self.load(load_from)

    # we use mobilenetv3 as an example, but you can use any model you want
    def get_network(weights=None):
        if weights:
            net = mobilenet_v3_small(weights=weights)
            net.classifier[3] = torch.nn.Linear(1024, 1)
        return mobilenet_v3_small(num_classes=1)

    def forward(self, x):
        return self.net(x)

    def load(self, path):
        self.net.load_state_dict(torch.load(path))

    def save(self, path):
        torch.save(self.net.state_dict(), path)

def train_epoch(predictor, optimizer, dataloader, exp_avg=0.1):  # simple supervised learning, could be semi-supervised too
    predictor.net.train()
    criterion = torch.nn.BCEWithLogitsLoss()  # modify if needed
    running_loss = 0
    with tqdm.tqdm(total=len(dataloader)) as pbar:
        for i, (imgind, img, label) in enumerate(dataloader):
            optimizer.zero_grad()
            y_hat = predictor(img)
            loss = criterion(y_hat, label)
            loss.backward()
            optimizer.step()
            running_loss = loss.item() if running_loss == 0 else ((1-exp_avg) * running_loss + exp_avg * loss.item())
            pbar.update(1)
            pbar.set_postfix({"loss": running_loss, "batch": i})
    return predictor, optimizer

def continuously_train(lr=0.001, batch_size=32, exp_avg=0.1, load_from=None):
    """Train continuously. Updates the dataset after each epoch."""
    predictor = Predictor(load_from=load_from)  # load_from if using self-supervised learning
    optimizer = torch.optim.Adam(predictor.net.parameters(), lr=lr)
    full_dataset = FullDataset(annotation_file=annfilepath, datadir=datadir)
    while True:
        full_dataset.refresh()
        labeled_ds = LabeledDataset(full_dataset)
        dataloader = DataLoader(labeled_ds, batch_size=batch_size, shuffle=True, num_workers=4, drop_last=False)  # we're using dynamic shapes but torch2.0 can be made faster without them
        predictor, optimizer = train_epoch(predictor, optimizer, dataloader, exp_avg=exp_avg)
        predictor.save(ckptpath)




def pretrain_oracular(dstfile='oracular.pt', n_epochs=10, batch_size=32, lr=0.001):
    predictor = Predictor(load_from=dstfile)
    predictor.net.train()
    optimizer = torch.optim.Adam(predictor.net.parameters(), lr=lr)
    criterion = torch.nn.BCEWithLogitsLoss()
    dataset = CatsAndDogsDataset('../archive/kagglecatsanddogs_3367a/PetImages/')
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4, drop_last=True)
    for epoch_idx in range(n_epochs):
        running_loss = 0
        with tqdm.tqdm(total=len(dataloader), desc=f"Epoch {epoch_idx}") as pbar:
            for i, (imgind, img, label) in enumerate(dataloader):
                optimizer.zero_grad()
                y_hat = predictor(img)
                loss = criterion(y_hat, label)
                loss.backward()
                optimizer.step()
                running_loss = loss.item() if running_loss == 0 else (0.9 * running_loss + 0.1 * loss.item())
                pbar.update(1)
                pbar.set_postfix({"loss": running_loss, "batch": i})
        predictor.save(f'oracular_{epoch_idx}.pt')



def seed_everything(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

if __name__ == '__main__':
    SEED = 0
    seed_everything(SEED)
    continuously_train(lr=0.001, batch_size=8, exp_avg=0.1, load_from=None)