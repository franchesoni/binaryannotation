# 🔥 Intelligent Annotation - Binary Classification 🔥
![_8f2ba80f-7689-4327-84f7-78d8d6e4bd5e](https://github.com/franchesoni/binaryannotation/assets/24411007/08b53d80-8a5e-4df9-84da-a0e6fac6c34b)
This tool allows you to more quickly annotate an image dataset with binary classes leveraging AI.
---
# FEATURES:
- 🤖 **active learning**
- 🤖 **automatic mode**
- 🖌️ **contrast & brightness** change
- 💾 **resume** annotation sessions
- 🚀 **export** your predictor
- ⏲️ online annotation **performance statistics**
  


# Summary
## Why should you use this app?
- 🪵 Our app is **MINIMALISTIC** because minimalism is the best we have come up with regarding annotation speed for binary classification of images. The extremely simple works great.
- 🧮 We have **considered lots of sophistication**: active learning, semi-supervised learning, showing images in batches, run length encoding, mathematically optimal orderings.
- 🏆 But we found that the good old **supervised learning** and **entropy** (balanced data) or **max-probability** (unbalanced data) active learning is the best. 🏆
- 🤗 On top, the best user experience is either labeling as positive or negative manually, or having the machine label everything as negative if you didn't say positive before some configurable time (the AUTO mode).
- 🎁 Because a model is trained continuously on the background to help you with Intelligent Annotation (IA), once you're done annotating or find that the model is always right, you can export it or let it annotate the whole data. Thus this is a **human-in-the-loop learning solution**.

## Our usecase
By default it's designed to annotate a large dataset of images with binary classes. In particular we assume that the positive class is the minority class.
As active learning, the entropy is an incredibly good baseline. However, we care about annotation speed, and we have found that the fastest way to annotate is to provide many samples from the same class. Because there is a minority class, we choose to show those samples first.

# USE:
first:
- make sure your python version has the packages in `requirements.txt` installed
- (if running remote) ssh tunnel your desired ports to your machine
- clone the repo and open it
- run the following commands (assuming Linux)
  ```
  cd backend
  # # to know how it works:
  bash launch.sh  
  # # to run the annotation of folder `path/to/your/data` at ports 8077 and 8078 (tensorboard), without resetting and with AI training on the background
  bash launch.sh localhost 8077 false path/to/your/data false examplerunname false
  ```
  _note: docker mode is not available at the moment_
- annotate
- open issues for any question

# DEV
### frontend
- modify the code in `reactcode/`
- get nvm (node version manager)

```
# use node 18 to build react code
cd reactcode
nvm use --lts 
npm install
npm run build2
```
### backend
It's just Python FastAPI. 


## Code structure
This app involves many modules and intercommunication between them. They're better understood from the file descriptions below. Customize them as needed, although we provide a potentially useful starting point.
For simplicity, we use pickle-based communication (with the exception of `torch.save`, which is similar).

We have:
- `config.py`: Defines useful variables such as `dev, device, datadir`, etc.. 
- `IA/dataset.py`: Implements `LabeledDataset` and `UnlabeledDataset` classes. Each class subclasses pytorch Dataset. Both list the files for each dataset. The first returns `imgindex, img, label` and the second returns `imgindex, img`. 
- `IA/training.py`: Has the predictor and the training functions that given a predictor update and save it. Here we can implement pretraining (e.g. self-supervised learning) and (semi-)supervised learning. **Here is where you define another network if you have one.**
- `IA/inference.py`: Runs inference over the dataset and saves the probabilities to a file.
- `IA/selector.py`: Loads the probabilities from the file and provides a ranking of files, indices and probabilities. **We use `max_prob` as a criterion by default.**
- `backend.py`: It serves the app, continuously reads the ranking and updates the annotations.

We implement file-based communication, in particular we store data in:
- `annfilepath = 'annotations.pickle'`: the annotations given by the user so far, written by `backend.py` and read by `training.py` and `inference.py`
- `ckptpath = 'predictor.ckpt'  # torch save, output of training`: the model as trained so far, written by `IA/training.py` and read by `IA/inference.py`.
- `predspath = 'predictions.pickle'  # a pickled dict, output of inference`: the predictions of the model over the unlabeled data, written by `IA/inference.py` and read by `IA/selector.py`
- `rankingpath = 'ranking.pickle'  # a pickled list, output of ranking`: the order in which to present the images, written by `IA/selector.py` and read by `backend.py`

This constitutes a sort of loop, but in fact all scripts are constantly running and checking if a new input file is present. In particular `IA/training.py` continuously trains even if the annotations haven't been updated.





