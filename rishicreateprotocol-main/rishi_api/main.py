from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, BackgroundTasks, Security
from fastapi.security import  OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import uuid
import zipfile
import replicate
import requests
from models import User, Job
from utils import create_access_token, get_db, authenticate_user, get_current_user, download_and_notify_training, download_and_notify_inference, authenticate_client, upload_to_cloudflare
from schema import Token, TrainingRequest, InferenceRequest
from datetime import timedelta
from sqlalchemy.orm import Session
from constants import REPLICATE_API_TOKEN, HOSTNAME, ACCESS_TOKEN_EXPIRE_MINUTES
import json

replicate.Client(api_token=REPLICATE_API_TOKEN)

app = FastAPI(
    title="Rishi API",
    description="Create protocol intenal GPU API",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Operations related to user authentication",
        },
        {
            "name": "utils",
            "description": "Operations related to utility functions",
        },
        {
            "name": "image",
            "description": "Endpoints for images model training and inference",
        },
        {
            "name": "jobs",
            "description": "Operations related to job management",
        },
    ]
)

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
data_dir = os.path.join(static_dir, "data")
images_dir = os.path.join(static_dir, "images")
loras_dir = os.path.join(static_dir, "loras")

os.makedirs(static_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)
os.makedirs(loras_dir, exist_ok=True)

# Mount the static directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Endpoints
@app.post("/auth/token", response_model=Token, tags=["authentication"]) 
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    if not authenticate_client(form_data.client_id, form_data.client_secret):
        raise HTTPException(status_code=400, detail="Incorrect client credentials")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": ["me"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/utils/zip-files",tags=["utils"])
async def zip_files(files: List[UploadFile] = File(...), current_user: User = Security(get_current_user, scopes=["me"])):
    zip_filename = f"{uuid.uuid4()}.zip"
    zip_path = os.path.join("static", "data", zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for file in files:
            content = await file.read()
            zip_file.writestr(file.filename, content)
    
    # Upload the zip file to Cloudflare R2 and get the public URL
    zip_url = upload_to_cloudflare(zip_path, f"raw/{zip_filename}")

    return {"zip_url": zip_url}

@app.post("/image/train",tags=["image"])
async def train_model(request: TrainingRequest, current_user: User = Security(get_current_user, scopes=["me"]), db: Session = Depends(get_db)):
    training = replicate.trainings.create(
        version="ostris/flux-dev-lora-trainer:9d960224bcfc17c68d621e7a6a5afb43d222588daa4e8ddc5f127e27ab874486",
        input={
            "steps": 1000,
            "lora_rank": 16,
            "optimizer": "adamw8bit",
            "batch_size": 1,
            "resolution": "512,768,1024",
            "autocaption": True,
            "input_images": request.file_url,
            "trigger_word": request.trigger_word,
            "learning_rate": 0.0004,
            "wandb_project": "flux_train_replicate",
            "wandb_save_interval": 100,
            "caption_dropout_rate": 0.05,
            "wandb_sample_interval": 100
        },
        destination=f"dipankar/two-model-merge",
        webhook=f"{HOSTNAME}/webhook",
    )
    job = Job(
        job_id=training.id,
        status="started",
        job_type="training",
        model=request.model,
        webhook=request.webhook,
        output="",
        meta_data=json.dumps({
            "trigger_word": request.trigger_word,
            "file_url": request.file_url
        })
    )
    db.add(job)
    db.commit()
    
    return {"job_id": training.id}

@app.post("/image/inference",tags=["image"])
async def run_inference(request: InferenceRequest, current_user: User = Security(get_current_user, scopes=["me"]), db: Session = Depends(get_db)):
    input_data = {
        "prompt": request.prompt,
        "hf_loras": request.lora_urls,
        "num_outputs": request.num_images
    }
    
    model = replicate.models.get("lucataco/flux-dev-multi-lora")
    version = model.versions.get("a738942df15c8c788b076ddd052256ba7923aade687b12109ccc64b2c3483aa1")
    prediction = replicate.predictions.create(
        version="a738942df15c8c788b076ddd052256ba7923aade687b12109ccc64b2c3483aa1",
        input=input_data,
        webhook=f"{HOSTNAME}/webhook",
    ) 
    
    job = Job(
        job_id=prediction.id,
        status="started",
        job_type="inference",
        model=request.model,
        webhook=request.webhook,
        output="",
        meta_data=json.dumps({
            "prompt": request.prompt,
            "lora_urls": request.lora_urls,
            "num_images": request.num_images
        })
    )
    db.add(job)
    db.commit()
    
    return {"job_id": prediction.id}

@app.post("/webhook",tags=["jobs"])
async def webhook(data: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    print(data) 
    job = db.query(Job).filter(Job.job_id == data["id"]).first()
    if job:
        job.status = data["status"]
        db.commit()
        
        if data["status"] == "succeeded":
            if job.job_type == "training":
                background_tasks.add_task(download_and_notify_training, data["output"]['weights'], job, db)
            elif job.job_type == "inference":
                background_tasks.add_task(download_and_notify_inference, data["output"], job, db)
    
    return {"status": "received"}

@app.get("/job-status/{job_id}",tags=["jobs"])
async def get_job_status(job_id: str, current_user: User = Security(get_current_user, scopes=["me"]), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if job:
        return {
            "status": job.status,
            "job_type": job.job_type,
            "model_name": job.model,
            "output": job.output,
            "meta_data": job.meta_data
        }
    raise HTTPException(status_code=404, detail="Job not found")