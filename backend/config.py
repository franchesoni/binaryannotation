dev = True

if dev:
    datadir = '../archive/kagglecatsanddogs_3367a/PetImages/'
else:
    datadir = '/archive/kagglecatsanddogs_3367a/PetImages/'

ckptpath = 'predictor.ckpt'  # torch save, output of training
annfilepath = 'annotations.pickle'  
predspath = 'predictions.pickle'  # a pickled dict, output of inference
rankingpath = 'ranking.pickle'  # a pickled list, output of ranking

