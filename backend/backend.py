"""Creates the backend using fastapi. The API is comprised by two endpoints: get_next_img and add_annotation."""
import fcntl
from pathlib import Path
import pickle
import threading

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from config import datadir, rankingpath, annfilepath
from dataset import FullDataset

class State:
    SEED = 0
    data_path = Path(datadir)

    def __init__(self):
        self.received_annotation = False
        self.dataset = FullDataset(State.data_path)
        self.annotations = {}
        self.ranking = None

state = State()
state_lock = threading.Lock()

def continuously_update_ranking(rankingpath=rankingpath):
    global state
    global state_lock

    last_modified = 0
    while True:
        if Path(rankingpath).is_file():
            modified_at = Path(rankingpath).stat().st_mtime
            if last_modified < modified_at:
                with open(rankingpath, 'rb') as f:
                    # Apply a shared lock on the file descriptor
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    # Read the data using pickle
                    ranking = pickle.load(f)  # {index: probability}
                    # Release the lock on the file descriptor
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

                state_lock.acquire()
                state.ranking = ranking
                state_lock.release()

                last_modified = modified_at
                    
process_thread = threading.Thread(target=continuously_update_ranking)
process_thread.start()

app = FastAPI(
    title='Cat or Dog?',
    description='A simple app to annotate images as cats or dogs.',
    version='0.1',
)

def get_image_path_given_index(image_index):
    assert image_index in state.indices
    return str(state.full_ds.files[image_index])

@app.get("/hello")
async def helloworld():
    return {"Hello": "World"}

@app.get('/get_next_img')
def get_next_img():
    for (ind, prob) in state.ranking:
        if ind not in state.annotations:
            break
    print('='*20)
    print('next_index', ind)
    # get the image path
    image_path = get_image_path_given_index(ind)
    state.received_annotation = False
    response = FileResponse(image_path, headers={"image_index": str(ind), "prob": str(prob)})
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.post('/add_annotation')
async def add_annotation(request: Request):
    global state
    global state_lock
    # get the image_index and is_positive from the request
    body = await request.json()
    image_index = int(body['image_index'])
    is_positive = bool(body['is_positive'])
    # add the image_index to the annotated_indices
    state_lock.acquire() 
    state.annotations[image_index] = is_positive
    # remove that index from the to_annotate_indices
    with open(annfilepath, 'wb') as f:
        # Apply an exclusive lock on the file descriptor
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        # Write the data using pickle
        pickle.dump(state.annotations, f)
        # Release the lock on the file descriptor
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


    state.received_annotation = True
    state_lock.release()
    print("="*20)
    print('state.annotations', state.annotations)
    return {'success': True}


templates = Jinja2Templates(directory="../frontend/")

app.mount("/", StaticFiles(directory="../frontend/", html=True), name="frontend")
@app.get("/")
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", context= {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

process_thread.join()