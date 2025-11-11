from fastapi import FastAPI, File, UploadFile,Request,Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import os

app=FastAPI(title="FastAPI Basics Tutorial")

#setup the logger
logging.basicConfig(level=logging.INFO)
log=logging.getLogger("tutorial")

#serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

#setup templates
templates=Jinja2Templates(directory="templates")

############ROutes########
#GET,POST,PUT,DELETE,PATCH,OPTIONS,HEAD

@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI Basics Tutorial"}

@app.get("/hello/{name}")
def greet_user(name: str, age: int = 20):
    return {"message": f"Hello {name}, you are {age} years old!"}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):

    if username == "admin" and password == "1234":
        return {"status": "success", "message": "Welcome, admin!"}
    return {"status": "fail", "message": "Invalid credentials"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save the uploaded file
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    log.info(f"File saved: {file_path}")
    return {"filename": file.filename, "saved_to": file_path}

@app.get("/ui", response_class=HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health_check():
    log.info("Health Check Passed")
    return {"status":"Ok"}

