from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from routes import proxy
from routes import examples
from utils import create_logger
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

logger = create_logger("app", ".logs/access.log")
app.mount("/static", StaticFiles(directory="frontend/assets"), name="static")
templates = Jinja2Templates(directory="frontend/pages")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    if "/proxy" in request.url.path:
        client_ip = request.client.host
        logger.info(f"Incoming request from {client_ip}: {request.method} {request.url}")
        response = await call_next(request)
        # logger.info(f"Response status code: {response.status_code}")
        return response
    else:
        return await call_next(request)

app.include_router(proxy.router, prefix="/proxy")
app.include_router(examples.router, prefix="/examples")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run("main:app", host=os.getenv("HOST"), port=int(os.getenv('PORT')), workers=1, reload=True)
    uvicorn.run("main:app", host=os.getenv("HOST"), port=int(os.getenv('PORT')), workers=1)

