# writing your custom app
This app involves many modules and intercommunication between them. They're better understood from the file descriptions below. Customize them as needed, although we provide a potentially useful starting point.
For simplicity, we use pickle-based communication (with the exception of `torch.save`, which is similar).

We have:
- `config.py`: Defines useful variables such as `dev, device, datadir`, etc.. 
- `IA/dataset.py`: Implements `LabeledDataset` and `UnlabeledDataset` classes. Each class subclasses pytorch Dataset. Both list the files for each dataset. The first returns `imgindex, img, label` and the second returns `imgindex, img`. 
- `IA/training.py`: Has the predictor and the training functions that given a predictor update and save it. Here we can implement pretraining (e.g. self-supervised learning) and (semi-)supervised learning.
- `IA/inference.py`: Runs inference over the dataset and saves the probabilities to a file.
- `IA/selector.py`: Loads the probabilities from the file and provides a ranking of files, indices and probabilities. 
- `backend.py`: It serves the app, continuously reads the ranking and updates the annotations.

We implement file-based communication, in particular we store data in:
- `annfilepath = 'annotations.pickle'`: the annotations given by the user so far, written by `backend.py` and read by `training.py`
- `ckptpath = 'predictor.ckpt'  # torch save, output of training`: the model as trained so far, written by `IA/training.py` and read by `IA/inference.py`.
- `predspath = 'predictions.pickle'  # a pickled dict, output of inference`: the predictions of the model over the unlabeled data, written by `IA/inference.py` and read by `IA/selector.py`
- `rankingpath = 'ranking.pickle'  # a pickled list, output of ranking`: the order in which to present the images, written by `IA/selector.py` and read by `backend.py`

This constitutes a sort of loop, but in fact all scripts are constantly running and checking if a new input file is present. In particular `IA/training.py` continuously trains even if the annotations haven't been updated.







# using docker
`docker build -t binaryannotation .`
`docker run -p 8000:8000 -v PATHTOFOLDERCONTAININGkagglecatsanddogs_3367a:/archive binaryannotation`

# dev (no docker)
given that everything is correctly installed, we do:
`python backend.py --reload`

download command (from get wget browser extension)
wget --header="Host: storage.googleapis.com" --header="User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0" --header="Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7" --header="Accept-Language: en,es-419;q=0.9,es;q=0.8,fr;q=0.7,pt-BR;q=0.6,pt;q=0.5" --header="Referer: https://www.kaggle.com/" "https://storage.googleapis.com/kaggle-data-sets/630856/1122723/bundle/archive.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20230525%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20230525T132759Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=681c6465ca6dce83498aba370371c2123a1914ba2a5ab5c27d458e4e96e8d2b98fbd5f8b622e0f284ce42ff08ec2031a975ff8a1ba36c6a44ef4a87f4517ab5996b97344569d4e943f0af6e746b06d5a99047eac6f96a81afa1e1dc04fa1465cae899bb1edded755a707d40379ce87ea93aa64bffab2f95800b7ac1fba278d267673cbd297e4bed7d7493aef61fb90bb7a2d9e2fc46906d851d474c429991187d77bfec3b1a608ed90eefb39a6e251349a9034c4be04149e099dc2f3671e3c4b2212258e39fbf992d7352539d4cf7e997bee9ad74ebab2a6140f19b54429c0da2c153d25c0e6856cfdb8ac402865852072b338afbed0b884d9c30fabf772cd90" -c -O 'archive.zip'
