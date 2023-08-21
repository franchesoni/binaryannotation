from pathlib import Path
import torch
dockermode=DOCKERMODEPLACEHOLDER
IPADDRESS='IPADDRESSPLACEHOLDER'
PORT='PORTPLACEHOLDER'
datadir = '/readonlydir/' if dockermode else 'DATADIRPLACEHOLDER'
dstdirpath = Path('DSTDIRPLACEHOLDER/' if dockermode else 'DSTDIRPLACEHOLDER')
Path(dstdirpath).mkdir(exist_ok=True)
ckptpath = str(dstdirpath / 'predictor.ckpt')  # torch save, output of training
logdir = str(dstdirpath / 'runs')
annfilepath = str(dstdirpath / 'annotations.pickle')
skippedfilepath = str(dstdirpath / 'skipped.pickle')
predspath = str(dstdirpath / 'predictions.pickle')  # a pickled dict, output of inference
rankingpath = str(dstdirpath / 'ranking.pickle')  # a pickled list, output of ranking
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
