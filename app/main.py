from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.routes import proxy
import os
from dotenv import load_dotenv
load_dotenv()
import logging

app = FastAPI()

# Create a logger for your application
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

# Create a file handler and set the logging level
file_handler = logging.FileHandler(".logs/access.log")
file_handler.setLevel(logging.DEBUG)

# Create a formatter and add it to the file handler
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

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


app.mount("/static", StaticFiles(directory="frontend/assets"), name="static")

templates = Jinja2Templates(directory="frontend/pages")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Add endpoint to downl;oad files in the ../examples folder
@app.get("/example/{file_path}")
async def read_examples(file_path: str):
    # get parent directory
    parent = os.path.dirname(os.path.dirname(__file__))
    file_path = f"{parent}/examples/{file_path}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "File not found."}

@app.get("/examples")
async def read_root():
    return {"message": "Hello World", "examples": [
        "/example/example_1.py",
        "/example/example_2.py",
        "/example/example_3.py",
        "/example/example_4.py",
    ]}

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run("main:app", host=os.getenv("HOST"), port=int(os.getenv('PORT')), workers=1, reload=True)
    uvicorn.run("main:app", host=os.getenv("HOST"), port=int(os.getenv('PORT')), workers=1)

