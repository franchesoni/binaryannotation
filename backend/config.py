import torch

dev = True

if dev:
    datadir = '/mnt/c/users/mrhal/desktop/stage/kagglecatsanddogs_3367a'
else:
    datadir = '/archive/kagglecatsanddogs_3367a/PetImages/'

ckptpath = 'predictor.ckpt'  # torch save, output of training
annfilepath = 'annotations.pickle'  
predspath = 'predictions.pickle'  # a pickled dict, output of inference
rankingpath = 'ranking.pickle'  # a pickled list, output of ranking

IPADDRESS = 'localhost'
PORT = '8000'
#DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
DEVICE = 'cpu' if torch.cuda.is_available() else 'cpu'
