print('importing packages in training.py')
import time
from pathlib import Path

import tqdm
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights
import torch
from torch.utils.data import DataLoader
from torch.utils.tensorboard.writer import SummaryWriter

from IA.dataset import FullDataset, LabeledDataset, UnlabeledDataset
from IA.iotofiles import safely_save_torch, safely_load_torch
from config import datadir, ckptpath, annfilepath, DEVICE
print('finished importing packages in training.py')



class Predictor(torch.nn.Module):  
    def __init__(self, load_from=None):
        super().__init__()
        if load_from is None:
            weights = MobileNet_V3_Small_Weights
            # weights = None
        elif Path(load_from).is_file():
            weights = None
        else:
            raise ValueError(f"load_from must be None or a file, not {load_from}")
        self.net = self.get_network(weights=weights)
        if (load_from is not None) and (Path(load_from).is_file()):
            self.load(load_from)
        self.net = self.net.to(DEVICE)
        # self.net = torch.compile(self.net, mode='reduce-overhead')

    # we use mobilenetv3 as an example, but you can use any model you want
    def get_network(self, weights=None):
        if weights:
            net = mobilenet_v3_small(weights=weights)
            net.classifier[3] = torch.nn.Linear(1024, 1)
            return net
        return mobilenet_v3_small(num_classes=1)

    def forward(self, x):
        return self.net(x)

    def load(self, path):
        self.net = safely_load_torch(self.net, path)

    def save(self, path):
        safely_save_torch(self.net, path)
        self.net = safely_load_torch(self.net, path)

swstep = 0
def train_epoch(predictor, optimizer, dataloader, summary_writer:SummaryWriter|None = None, exp_avg=0.1, epoch_n=0):  # simple supervised learning, could be semi-supervised too
    global swstep
    print('training epoch', end='\r')
    predictor.net.train()
    predictor.to(DEVICE)
    criterion = torch.nn.BCEWithLogitsLoss()  # modify if needed
    running_loss = 0
    with tqdm.tqdm(total=len(dataloader), disable=True) as pbar:
        # try:
            for i, (imgind, imgpath, img, label) in enumerate(dataloader):
                img, label = img.to(DEVICE), label.to(DEVICE)
                optimizer.zero_grad()
                y_hat = predictor(img).flatten()
                loss = criterion(y_hat, label*1.)
                loss.backward()
                optimizer.step()
                running_loss = loss.item() if running_loss == 0 else ((1-exp_avg) * running_loss + exp_avg * loss.item())
                pbar.update(1)
                pbar.set_postfix({"loss": running_loss, "batch": i})
                if summary_writer:
                    summary_writer.add_scalar('loss', loss.item(), swstep)
                    swstep += 1
        # except KeyError:
        #     print('key error')
        #     breakpoint()
    return predictor, optimizer

def continuously_train(lr=0.001, batch_size=32, exp_avg=0.1, load_from=None, annfilepath=annfilepath, ckptpath=ckptpath, maxbatches=None):
    """Train continuously. Updates the dataset after each epoch."""
    global swstep
    summary_writer = SummaryWriter()
    predictor = Predictor(load_from=load_from)  # load_from if using self-supervised learning
    optimizer = torch.optim.Adam(predictor.net.parameters(), lr=lr)
    full_dataset = FullDataset(annotation_file=annfilepath, datadir=datadir)
    while True:
        full_dataset.refresh()
        labeled_ds = LabeledDataset(full_dataset)
        if len(labeled_ds) == 0:
            print('No annotated data, waiting 1 second...')
            time.sleep(1)
            continue
        dataloader = DataLoader(labeled_ds, batch_size=batch_size, shuffle=True, num_workers=0, drop_last=False)  # we're using dynamic shapes but torch2.0 can be made faster without them
        predictor, optimizer = train_epoch(predictor, optimizer, dataloader, summary_writer=summary_writer, exp_avg=exp_avg)
        predictor.save(ckptpath)
        print(">>> checkpoint updated")
        if maxbatches and swstep > maxbatches:
            break




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