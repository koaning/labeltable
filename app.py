import random 

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, validator

from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")


def batch_generator():
    letters = "qwertyuiopasdfghjklzxcvbnm"
    while True:
        strings = ["".join(random.choice(letters) for i in range(5)) for j in range(6)]
        original_id = "".join(random.choice(letters) for i in range(10))
        yield {"original_id": original_id, "items": strings}

gen = batch_generator()

def create_app(batch_generator=batch_generator()):
    @app.get("/items/{id}", response_class=HTMLResponse)
    async def read_item(request: Request, id: str):
        batch = batch_generator()
        context = {"request": request, "strings": batch['items'], "id": id, "orig_id": batch['original_id']}
        return templates.TemplateResponse("labelview.html", context=context)


    @app.post("/submit")
    async def submit(request: Request, response_class=HTMLResponse):
        body = (await request.body()).decode("utf-8")
        items = [s.split("=") for s in body.split("&")]
        
        original_id = [i for i in items if i[0] == 'origid'][0][1]
        items = [i for i in items if i[0] != "origid"]
        selected = set([i[0] for i in items])
        checked = set([i[0] for i in items if i[1] == 'on'])
        unchecked = selected.difference(checked)

        for item in checked:
            print(f"{item},{original_id},1")
        for item in unchecked:
            print(f"{item},{original_id},0")

        batch = batch_generator()
        context = {"request": request, "strings": batch['items'], "id": id, "orig_id": batch['original_id']}
        return templates.TemplateResponse("labeltable.html", context=context)

