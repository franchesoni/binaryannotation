dev = False

if dev:
    datadir = '../archive/kagglecatsanddogs_3367a/PetImages/'
else:
    datadir = '/archive/kagglecatsanddogs_3367a/PetImages/'

ckptpath = 'predictor.ckpt'  # torch save, output of training
annfilepath = 'annotations.pickle'  
predspath = 'predictions.pickle'  # a pickled dict, output of inference
rankingpath = 'ranking.pickle'  # a pickled list, output of ranking

IPADDRESS = '0.0.0.0'# if dev else '138.231.63.90'
PORT = '8000'# if dev else '2332'
