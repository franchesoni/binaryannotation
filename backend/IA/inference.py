print('importing packages in inference.py')
import time
import os
from pathlib import Path

import tqdm
import torch
from torch.utils.data import DataLoader

from config import DEVICE, ckptpath, annfilepath, datadir, predspath
from IA.training import Predictor
from IA.dataset import FullDataset, UnlabeledDataset
from IA.iotofiles import safely_write
print('finished importing packages in inference.py')

def continuously_infer(ckptpath=ckptpath, batch_size=32):
    print('starting continuously_infer...')
    last_modified = 0
    full_ds = FullDataset(annotation_file=annfilepath, datadir=datadir)
    while True:
        if Path(ckptpath).is_file():
            modified_at = Path(ckptpath).stat().st_mtime
            if last_modified < modified_at:
                # print('infering 0...')
                predictor = Predictor(load_from=ckptpath).to(DEVICE)
                predictor.net.eval()
                # print('infering 1...')
                full_ds.refresh()
                # print('infering 2...')
                # data
                n_labeled = len(full_ds.annotated_paths)
                unlabeled_ds = UnlabeledDataset(full_ds)
                dataloader = DataLoader(unlabeled_ds, batch_size=batch_size, shuffle=False, num_workers=0, drop_last=False)
                print(f'infering 3... ({n_labeled} images)')

                # inference
                with torch.no_grad():
                    preds = - torch.ones(len(unlabeled_ds), device=DEVICE)  # placeholder with -1
                    with tqdm.tqdm(total=n_labeled // batch_size, desc='inference'
                    ) as pbar:
                        for i, (imgind, imgpath, img) in enumerate(dataloader):
                            img = img.to(DEVICE)
                            y_hat = torch.sigmoid(predictor(img))
                            preds[i*batch_size:(i+1)*batch_size] = y_hat[:, 0]
                            pbar.update(1)
                            pbar.set_postfix({"batch": i})
                            if i >= n_labeled // batch_size:
                                break
                # print('infering 4...')

                # save predictions
                paths = full_ds.to_annotate_paths
                preds = dict(zip(paths, preds.tolist()))
                safely_write(predspath, preds)
                print(">>> predictions updated")
                if i != n_labeled:  # only stop the loop if we have inferred all unlabeled images
                    last_modified = modified_at
            else:
                print('inference: checkpoint not modified')
                time.sleep(1)
        else:
            print('inference: waiting for checkpoint...')
            time.sleep(1)
                    


if __name__ == "__main__":
    continuously_infer()
