from pathlib import Path

import tqdm
import torch
from torch.utils.data import DataLoader

from config import ckptpath, annfilepath, datadir, predspath
from IA.training import Predictor
from IA.dataset import FullDataset, UnlabeledDataset
from IA.iotofiles import safely_write

def continuously_infer(ckptpath=ckptpath, batch_size=32):
    last_modified = 0
    full_ds = FullDataset(annotation_file=annfilepath, datadir=datadir)
    while True:
        if Path(ckptpath).is_file():
            modified_at = Path(ckptpath).stat().st_mtime
            if last_modified < modified_at:
                predictor = Predictor(load_from=ckptpath)
                # do inference
                full_ds.refresh()
                unlabeled_ds = UnlabeledDataset(full_ds)
                dataloader = DataLoader(unlabeled_ds, batch_size=batch_size, shuffle=False, num_workers=4, drop_last=False)
                preds = torch.empty(len(unlabeled_ds))
                predictor.net.eval()
                with tqdm.tqdm(total=len(dataloader)) as pbar:
                    for i, (imgind, img) in enumerate(dataloader):
                        y_hat = predictor(img)
                        preds[i*batch_size:(i+1)*batch_size] = y_hat[:, 0]
                        pbar.update(1)
                        pbar.set_postfix({"batch": i})
                # save predictions
                indices = full_ds.to_annotate_indices
                preds = dict(zip(indices, preds.tolist()))
                safely_write(predspath, preds)
                last_modified = modified_at
                    


if __name__ == "__main__":
    continuously_infer()