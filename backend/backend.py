"""Creates the backend using fastapi. The API is comprised by two endpoints: get_next_img and add_annotation."""
print('importing packages in backend.py')
from pathlib import Path
import threading
import time
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from config import datadir, rankingpath, annfilepath, skippedfilepath, IPADDRESS, PORT
from IA.dataset import FullDataset
from IA.iotofiles import safely_write, safely_read
from IA.selector import init_ranking
print('finished importing packages in backend.py')

class State:
    SEED = 0
    data_path = Path(datadir)


    def __init__(self):
        self.received_annotation = False
        self.dataset = FullDataset(annotation_file=annfilepath, skipped_file=skippedfilepath, datadir=str(State.data_path))
        self.annotations = {}
        self.skipped_annotations = []
        self.annotated = []
        self.next_to_annotate: tuple[str, int] | None = None
        self.ranking: list | None = None

state = State()
state_lock = threading.Lock()
update_ranking = True


def continuously_update_ranking(rankingpath=rankingpath):
    global state
    global state_lock

    last_modified = 0
    while update_ranking:
        if Path(rankingpath).is_file():
            modified_at = Path(rankingpath).stat().st_mtime
            if last_modified < modified_at:
                ranking = safely_read(rankingpath)
                state_lock.acquire()
                state.ranking = ranking
                state_lock.release()

                last_modified = modified_at
        else:
            init_ranking(state, rankingpath)
    print("interrupted ranking updates")


process_thread = threading.Thread(target=continuously_update_ranking)
process_thread.start()

app = FastAPI(
    title="Cat or Dog?",
    description="A simple app to annotate images as cats or dogs.",
    version="0.1",
)


@app.get("/hello")
async def helloworld():
    return {"Hello": "World"}


@app.get("/get_next_img")
def get_next_img():
    global state
    global state_lock
    seconds = 0
    while state.ranking is None:
        print(f'been waiting for ranking for {seconds}s...')
        seconds += 1
        time.sleep(1)
    for (image_path, prob) in state.ranking:  # get image from ranking
        if image_path not in state.annotations:
            break
    print('======================================')
    print(image_path)
    return return_path_prob(image_path, prob)

def return_path_prob(image_path: str, prob:int):
    global state
    global state_lock
    # get the image path
    state_lock.acquire()
    state.received_annotation = False
    state.next_to_annotate = (image_path, prob)
    state_lock.release()
    response = FileResponse(
        image_path, headers={"image_path": image_path, "prob": str(prob)}
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.post("/add_annotation")
async def add_annotation(request: Request):
    global state
    global state_lock
    # get the image_index and is_positive from the request
    body = await request.json()
    image_path = body['image_path']
    is_positive = bool(body['is_positive'])
    is_skipped = bool(body['is_skipped'])
    print('====================================')
    print(is_skipped)
    assert state.next_to_annotate is not None, "this variable should have been set in the last get_next_image call"  # make sure we call get_next_img or undo_annotation before
    assert state.next_to_annotate[0] == image_path, "new annotation should be on the last image got"  # make sure we call get_next_img or undo_annotation before
    state_lock.acquire()
    if (is_skipped == True):
        state.skipped_annotations.append(image_path)
        state.next_to_annotate = None
    else:
        # add the image_index to the annotated_indices
        state.annotated = state.annotated + [state.next_to_annotate]
        state.next_to_annotate = None
        assert state.annotated[-1] is not None, "you shouldn't overwrite an element referenced elsewhere"
        state.annotations[image_path] = is_positive
    state.received_annotation = True
    state_lock.release()
    safely_write(annfilepath, state.annotations)
    safely_write(skippedfilepath, state.skipped_annotations)
    # print("="*20)
    # print('state.annotations', state.annotations)
    return {"success": True}

@app.get('/reset_everything')
async def reset_everything(request: Request):
    #add the tab with the annotated image to the tab with all the index
    global state
    global state_lock
    state_lock.acquire()
    #clear the tab with the annotated image
    state.annotated = []
    #clear the json
    state.annotations = {}
    state_lock.release()
    safely_write(annfilepath, state.annotations)


@app.get('/undo_annotation')
async def undo_annotation():
    global state
    global state_lock
    #store the annotated image index in a tab (not in this function)
    #take the last one
    previous_image_path, previous_prob = state.annotated[-1]
    #delete the annotation
    assert previous_image_path in state.annotations, "previous index should be among the annotations"    
    state_lock.acquire()
    state.annotated = state.annotated[:-1]
    state.next_to_annotate = None
    del state.annotations[previous_image_path]
    state_lock.release()
    safely_write(annfilepath, state.annotations)
    #send path and index to front
    return return_path_prob(previous_image_path, previous_prob)



@app.get("/count_images")
def count_images():
    try:
        num_images = len(state.dataset)  
        return {"folder_path": Path(datadir), "num_images": num_images}
    except FileNotFoundError:
        return {"error": "Le chemin du dossier est introuvable."}
    except Exception as e:
        return {"error": str(e)}

templates = Jinja2Templates(directory="../frontend/")

app.mount("/", StaticFiles(directory="../frontend/", html=True), name="frontend")


@app.get("/")
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


if __name__ == "__main__":
    print('='*20)
    print(f'starting backend at http://{IPADDRESS}:{PORT}')
    import uvicorn
    uvicorn.run(app, host=IPADDRESS, port=int(PORT))

if process_thread.is_alive():
    update_ranking = False
    time.sleep(0.1)
print("still alive?", process_thread.is_alive())
