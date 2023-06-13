"""Creates the backend using fastapi. The API is comprised by two endpoints: get_next_img and add_annotation."""
from pathlib import Path
import threading
import time

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from config import datadir, rankingpath, annfilepath
from IA.dataset import FullDataset
from IA.iotofiles import safely_write, safely_read
from IA.selector import init_ranking


class State:
    SEED = 0
    data_path = Path(datadir)

    def __init__(self):
        self.received_annotation = False
        self.dataset = FullDataset(annotation_file=annfilepath, datadir=State.data_path)
        self.annotations = {}
        self.ranking = None


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


def get_image_path_given_index(image_index):
    assert image_index in state.dataset.to_annotate_indices
    return str(state.dataset.files[image_index])


@app.get("/hello")
async def helloworld():
    return {"Hello": "World"}


@app.get("/get_next_img")
def get_next_img():
    for (ind, prob) in state.ranking:
        if ind not in state.annotations:
            break
    ind = int(ind)
    print("prob", prob, "next_index", ind)
    # get the image path
    image_path = get_image_path_given_index(ind)
    state.received_annotation = False
    response = FileResponse(
        image_path, headers={"image_index": str(ind), "prob": str(prob)}
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.post("/add_annotation")
async def add_annotation(request: Request):
    global state
    global state_lock
    # get the image_index and is_positive from the request
    body = await request.json()
    image_index = int(body["image_index"])
    is_positive = bool(body["is_positive"])
    # add the image_index to the annotated_indices
    state_lock.acquire()
    state.annotations[image_index] = is_positive
    state.received_annotation = True
    state_lock.release()
    safely_write(annfilepath, state.annotations)
    # print("="*20)
    # print('state.annotations', state.annotations)
    return {"success": True}


templates = Jinja2Templates(directory="../frontend/")

app.mount("/", StaticFiles(directory="../frontend/", html=True), name="frontend")


@app.get("/")
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

if process_thread.is_alive():
    update_ranking = False
    time.sleep(0.1)
print("still alive?", process_thread.is_alive())
