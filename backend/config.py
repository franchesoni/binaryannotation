from pathlib import Path
import torch
dockermode=DOCKERMODEPLACEHOLDER
IPADDRESS='IPADDRESSPLACEHOLDER'
PORT='PORTPLACEHOLDER'
datadir = '/readonlydir/' if dockermode else 'DATADIRPLACEHOLDER'
iodirpath = Path('/iodir/' if dockermode else 'iodir/')
Path(iodirpath).mkdir(exist_ok=True)
ckptpath = str(iodirpath / 'predictor.ckpt')  # torch save, output of training
logdir = str(iodirpath / 'runs')
annfilepath = str(iodirpath / 'annotations.pickle')
skippedfilepath = str(iodirpath / 'skipped.pickle')
predspath = 'predictions.pickle'  # a pickled dict, output of inference
rankingpath = 'ranking.pickle'  # a pickled list, output of ranking
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
