"""Creates the backend using fastapi. The API is comprised by two endpoints: get_next_img and add_annotation."""
import os
import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from dataset import CatsAndDogsDataset 
from selector import MinProbSelector as Selector

class State:
    SEED = 0
    # data_path = Path('/archive/kagglecatsanddogs_3367a/PetImages/')
    data_path = Path('../archive/kagglecatsanddogs_3367a/PetImages/')

    def __init__(self):
        self.received_annotation = False
        self.dataset = CatsAndDogsDataset(State.data_path)
        self.files = self.dataset.files
        self.indices = list(range(len(self.files)))
        self.to_annotate_indices = set(self.indices)
        self.annotations = {}

state = State()
selector = Selector(state)

app = FastAPI(
    title='Cat or Dog?',
    description='A simple app to annotate images as cats or dogs.',
    version='0.1',
)

def get_image_path_given_index(image_index):
    assert image_index in state.indices
    return str(state.files[image_index])

@app.get("/hw")
async def read_root2():
    return {"Hello": "World"}

@app.get('/get_next_img')
def get_next_img():
    next_index, prob = selector.get_next_img(state)
    print('='*20)
    print('next_index', next_index)
    print('='*20)
    # get the image path
    image_path = get_image_path_given_index(next_index)
    state.received_annotation = False
    response = FileResponse(image_path, headers={"image_index": str(next_index), "prob": str(prob)})
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


templates = Jinja2Templates(directory="../frontend/")

app.mount("/", StaticFiles(directory="../frontend/", html=True), name="frontend")
@app.get("/")
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", context= {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)