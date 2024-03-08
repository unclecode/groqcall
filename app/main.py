from fastapi import FastAPI
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

# class RequestLoggingMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         print(f"Incoming request: {request.method} {request.url}")
#         print(f"Request headers: {request.headers}")
#         print(f"Request body: {await request.body()}")
#         response = await call_next(request)
#         return response

# app.add_middleware(RequestLoggingMiddleware)

app.include_router(proxy.router, prefix="/proxy")

# Add endpoint to downl;oad files in the ../examples folder
@app.get("/examples/{file_path}")
async def read_examples(file_path: str):
    # get parent directory
    parent = os.path.dirname(os.path.dirname(__file__))
    file_path = f"{parent}/examples/{file_path}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "File not found."}

@app.get("/")
async def read_root():
    return {"message": "Hello World", "examples": [
        "/examples/example_1.py",
        "/examples/example_2.py",
        "/examples/example_3.py",
        "/examples/example_4.py",
    ]}

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run("main:app", host=os.getenv("HOST"), port=int(os.getenv('PORT')), workers=1, reload=True)
    uvicorn.run("main:app", host=os.getenv("HOST"), port=int(os.getenv('PORT')), workers=1)

