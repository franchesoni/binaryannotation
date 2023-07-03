import torch
datadir = '/readonlydir/'
ckptpath = '/iodir/predictor.ckpt'  # torch save, output of training
logdir = '/iodir/runs/'
annfilepath = '/iodir/annotations.pickle'  
predspath = 'predictions.pickle'  # a pickled dict, output of inference
rankingpath = 'ranking.pickle'  # a pickled list, output of ranking
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
IPADDRESS = '0.0.0.0'
PORT = '8077'