"""Creates the backend using fastapi. The API is comprised by two endpoints: get_next_img and add_annotation."""
import os
import json
from pathlib import Path
import random

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from fastapi.templating import Jinja2Templates

class State:
    SEED = 0
    #data_path = Path('/images/PetImages/')
    data_path = Path('../../kagglecatsanddogs3367a/PetImages/')


    def __init__(self):
        self.received_annotation = False
        self.files = [State.data_path / 'Cat' / file for file in os.listdir(State.data_path / 'Cat')]  + [State.data_path / 'Dog' / file for file in os.listdir(State.data_path / 'Dog')]
        self.indices = list(range(len(self.files)))
        self.to_annotate_indices = set(self.indices)
        self.annotations = {}
        self.annotated = list()

state = State()
random.seed(State.SEED)

app = FastAPI(
    title='Cat or Dog?',
    description='A simple app to annotate images as cats or dogs.',
    version='0.1',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=['Image_index'],
)
def get_image_path_given_index(image_index):
    assert image_index in state.indices
    return str(state.files[image_index])

@app.get("/hw")
async def read_root2():
    return {"Hello": "World"}

@app.get('/get_next_img')
def get_next_img():
    # randomly sample an index from the to_annotate_indices
    next_index = random.sample(list(state.to_annotate_indices), 1)[0]
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
    #test
    state.annotated.append(image_index)
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

@app.get('/reset_annotation')
async def reset_annotation(request: Request):
    print(state.annotated)
    #add the tab with the annotated image to the tab with all the index
    state.to_annotate_indices = state.to_annotate_indices.union(state.annotated)
    #clear the tab with the annotated image
    state.annotated.clear()
    #clear the json
    state.annotations.clear()
    with open('annotations.json', 'w') as f:
        json.dump(state.annotations, f)
    return

@app.get('/undo_annotation')
async def undo_annotation():
    #store the annotated image index in a tab (not in this function)
    #take the last one
    image_index = state.annotated[-1]
    #get_image_path_given_index(last_one)
    image_path = get_image_path_given_index(image_index)
    #delete the annotation
    del state.annotated[-1]
    keys = list(state.annotations.keys())
    if keys:
        last_key = keys[-1]
        del state.annotations[last_key]
    with open('annotations.json', 'w') as f:
        json.dump(state.annotations, f)
    #send path and index to front
    response = FileResponse(image_path, headers={"image_index": str(image_index)})
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

templates = Jinja2Templates(directory="../frontend/")

app.mount("/", StaticFiles(directory="../frontend/", html=True), name="frontend")
@app.get("/")
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", context= {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)