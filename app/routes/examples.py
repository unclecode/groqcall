
from fastapi.responses import FileResponse
from fastapi import APIRouter
import os

router = APIRouter()

# Add endpoint to downl;oad files in the ../examples folder
@router.get("/{file_path}")
async def read_examples(file_path: str):
    # get parent directory
    parent = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = f"{parent}/examples/{file_path}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "File not found."}

# @router.get("/examples")
# async def read_root():
#     return {"message": "Hello World", "examples": [
#         "/example/example_1.py",
#         "/example/example_2.py",
#         "/example/example_3.py",
#         "/example/example_4.py",
#     ]}