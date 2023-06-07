from pathlib import Path

import tqdm
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights
import torch
from torch.utils.data import DataLoader

from dataset import CatsAndDogsDataset


class Predictor(torch.nn.Module):
    def __init__(self, load_from=None):
        super().__init__()
        if Path(load_from).is_file():
            self.net = mobilenet_v3_small()
        else:
            self.net = mobilenet_v3_small(weights=MobileNet_V3_Small_Weights)
        self.net.classifier[3] = torch.nn.Linear(1024, 2)
        if Path(load_from).is_file():
            self.load(load_from)

    def forward(self, x):
        return self.net(x)

    def load(self, path):
        self.net.load_state_dict(torch.load(path))

    def save(self, path):
        torch.save(self.net.state_dict(), path)

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
    pretrain_oracular(n_epochs=1)