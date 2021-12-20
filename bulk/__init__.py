import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


def _parse_rq_items(items):
    """Takes the items from the query-string and turns them into a list of labelled dictionaries"""
    original_id = [i for i in items if i[0] == "origid"][0][1]
    items = [i for i in items if i[0] != "origid"]
    selected = set([i[0] for i in items])
    checked = set([i[0] for i in items if i[1] == "on"])
    unchecked = selected.difference(checked)

    results = []
    for item in checked:
        results.append({"item": item, "original_id": original_id, "label": 1})
    for item in unchecked:
        results.append({"item": item, "original_id": original_id, "label": 0})
    return results


def create_app(batch_generator=None, outfile="labels.jsonl", templates_dir="templates"):
    """Creates an app that allows you to bulk label items."""
    templates = Jinja2Templates(directory=templates_dir)

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """The landing page of the app."""
        batch = next(batch_generator)
        context = {
            "request": request,
            "strings": batch["items"],
            "orig_id": batch["original_id"],
        }
        return templates.TemplateResponse("labelview.html", context=context)

    @app.post("/submit")
    async def submit(request: Request, response_class=HTMLResponse):
        """The endpoint to submit data. Writes to logfile and creates new form."""
        body = (await request.body()).decode("utf-8")
        items = [s.split("=") for s in body.split("&")]

        # Store the labels locally
        labels = _parse_rq_items(items)
        with open(outfile, "a") as f:
            for label in labels:
                f.write(json.dumps(label) + "\n")

        # Make a new batch for htmx
        batch = next(batch_generator)
        context = {
            "request": request,
            "strings": batch["items"],
            "id": id,
            "orig_id": batch["original_id"],
        }
        return templates.TemplateResponse("labeltable.html", context=context)

    return app
