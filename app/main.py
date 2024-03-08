from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.routes import proxy
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

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

