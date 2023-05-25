"""Creates the backend using fastapi. The API is comprised by two endpoints: get_next_img and add_annotation."""
import os
import json
from pathlib import Path
import random
from fastapi import FastAPI
from fastapi.responses import FileResponse

SEED = 0
random.seed(SEED)


data_path = Path('archive/kagglecatsanddogs_3367a/PetImages/')
files = os.listdir(data_path / 'Cat') + os.listdir(data_path / 'Dog')
indices = list(range(len(files)))
to_annotate_indices = set(indices)
annotations = {}

app = FastAPI()

def get_image_path_given_index(image_index):
    assert image_index in indices
    return files[image_index]


@app.get('/get_next_img')
def get_next_img():
    # randomly sample an index from the to_annotate_indices
    next_index = random.sample(to_annotate_indices, 1)[0]
    # get the image path
    image_path = get_image_path_given_index(next_index)
    return {'image_file': FileResponse(image_path), 'image_index': next_index}


@app.post('/add_annotation')
def add_annotation(image_index: int, is_positive: bool):
    # add the image_index to the annotated_indices
    annotations[image_index] = is_positive
    # remove that index from the to_annotate_indices
    to_annotate_indices.remove(image_index)
    with open('annotations.json', 'w') as f:
        json.dump(annotations, f)
    return {'success': True}
