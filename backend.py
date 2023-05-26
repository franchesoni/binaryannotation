"""Creates the backend using fastapi. The API is comprised by two endpoints: get_next_img and add_annotation."""
import os
import json
from pathlib import Path
import random

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

class State:
    SEED = 0
    data_path = Path('archive/kagglecatsanddogs_3367a/PetImages/')

    def __init__(self):
        self.received_annotation = False
        self.files = [State.data_path / 'Cat' / file for file in os.listdir(State.data_path / 'Cat')]  + [State.data_path / 'Dog' / file for file in os.listdir(State.data_path / 'Dog')]
        self.indices = list(range(len(self.files)))
        self.to_annotate_indices = set(self.indices)
        self.annotations = {}

state = State()
random.seed(State.SEED)

app = FastAPI(
    title='Cat or Dog?',
    description='A simple app to annotate images as cats or dogs.',
    version='0.1',
)

app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

def get_image_path_given_index(image_index):
    assert image_index in state.indices
    return str(state.files[image_index])

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/hw")
async def read_root2():
    return {"Hello": "World2"}

@app.get('/get_next_img')
def get_next_img():
    # randomly sample an index from the to_annotate_indices
    next_index = random.sample(state.to_annotate_indices, 1)[0]
    print('='*20)
    print('next_index', next_index)
    print('='*20)
    # get the image path
    image_path = get_image_path_given_index(next_index)
    state.received_annotation = False
    response = FileResponse(image_path, headers={"image_index": str(next_index)})
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.post('/add_annotation')
async def add_annotation(request: Request):
    # get the image_index and is_positive from the request
    body = await request.json()
    image_index = int(body['image_index'])
    is_positive = bool(body['is_positive'])
    # add the image_index to the annotated_indices
    state.annotations[image_index] = is_positive
    # remove that index from the to_annotate_indices
    if image_index in state.to_annotate_indices:
        state.to_annotate_indices.remove(image_index)
    with open('annotations.json', 'w') as f:
        json.dump(state.annotations, f)
    state.received_annotation = True
    print("="*20)
    print('state.annotations', state.annotations)
    print("="*20)
    return {'success': True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)