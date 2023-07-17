import pickle
from IA.training import Predictor
from IA.dataset import FullDataset



def main():
    ds = FullDataset('dummypath', '../archive')
    ds.labels = ['Dog' in str(f) for f in ds.files]
    for n_ann in [10, 20, 50, 100, 200, 500]:
        print(f'Number of annotations: {n_ann}')
        annotations = {i: l for i, l in zip(ds.indices[:n_ann], ds.labels[:n_ann])}
        with open(f'annotations_{n_ann}.pickle', 'wb') as f:
            pickle.dump(annotations, f)
    


    breakpoint()
    pass


if __name__ == '__main__':
    main()