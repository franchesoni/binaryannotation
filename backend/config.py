import torch

dev = False

if dev:
    # datadir = '/mnt/c/users/basti/desktop/stage/kagglecatsanddogs3367a/PetImages'
    datadir = '/home/franchesoni/bastien/archive'
else:
    datadir = '/archive/kagglecatsanddogs_3367a/PetImages/'

if dev:
    ckptpath = 'predictor.ckpt'  # torch save, output of training
    annfilepath = 'annotations.pickle'  
else:
    ckptpath = '/results/predictor.ckpt'  # torch save, output of training
    annfilepath = '/results/annotations.pickle'  

predspath = 'predictions.pickle'  # a pickled dict, output of inference
rankingpath = 'ranking.pickle'  # a pickled list, output of ranking

IPADDRESS = '0.0.0.0'
PORT = '8000'
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
