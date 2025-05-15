from fastapi import Depends, HTTPException
from models import User, Job
from database import SessionLocal
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import requests
import uuid
import os
from typing import List
from schema import TokenData
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from constants import SECRET_KEY, ALGORITHM, CLIENT_ID, CLIENT_SECRET, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ENDPOINT, R2_BUCKET_NAME, R2_BASE_URL
import json

import json
import tarfile
from datetime import datetime
from shutil import move

import boto3
from botocore.config import Config
from typing import Optional

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Helper functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_client(client_id: str, client_secret: str):
    if client_id == CLIENT_ID and client_secret == CLIENT_SECRET:
        return True
    return False

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=401,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user

def download_and_notify_training(output_url: str, job: Job, db: Session):
    # Download weights
    response = requests.get(output_url)
    tar_path = os.path.join("static", "loras", f"{job.job_id}.tar")
    os.makedirs(os.path.dirname(tar_path), exist_ok=True)
    with open(tar_path, 'wb') as f:
        f.write(response.content)

    # Extract lora.safetensors file
    extract_dir = os.path.join("tmp", "rishi-api" , job.job_id)
    os.makedirs(extract_dir, exist_ok=True)
    with tarfile.open(tar_path, 'r') as tar:
        tar.extractall(path=extract_dir)

    # Find and rename lora.safetensors
    src_file = os.path.join(extract_dir, "output", "flux_train_replicate", "lora.safetensors")
    dst_file = os.path.join("static", "loras", f"{job.job_id}.safetensors")

    # Upload the weights to Cloudflare R2
    upload_to_cloudflare(tar_path, f"tar/{job.job_id}.tar")

    # Upload the safetensors to Cloudflare R2
    r2_url = upload_to_cloudflare(src_file, f"safetensors/{job.job_id}.safetensors")

    # Clean up: remove the extracted directory
    os.system(f"rm -rf {extract_dir}")

    # Update job status
    job.output = json.dumps({"lora_weights": r2_url})
    job.completed_at = datetime.now()
    
    db.add(job)
    db.commit()
    db.refresh(job)

    # Notify user's webhook
    requests.post(job.webhook, json={
        "status": "completed",
        "job_type": "training",
        "model_name": job.model,
        "output": dst_file,
        "meta_data": job.meta_data
    })

def download_and_notify_inference(output_urls: List[str], job: Job, db: Session):
    # Download and save output images
    image_paths = []
    for i, image_url in enumerate(output_urls):
        image_filename = f"{uuid.uuid4()}.png"
        image_path = os.path.join("static", "images", image_filename)
        response = requests.get(image_url)
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        # Upload the image to Cloudflare R2
        image_url = upload_to_cloudflare(image_path, f"images/{image_filename}")
        image_paths.append(image_url)
    
    # Update job status
    job.output = json.dumps({"images":image_paths})
    job.completed_at = datetime.now()
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Notify user's webhook
    requests.post(job.webhook, json={
        "status": "completed",
        "job_type": "inference",
        "model_name": job.model,
        "output": image_paths,
        "meta_data": job.meta_data
    })

# Configure the S3 client for Cloudflare R2
s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    config=Config(signature_version="s3v4"),
)

def upload_to_cloudflare(file_path: str, object_name: Optional[str] = None) -> str:
    """
    Upload a file to Cloudflare R2, return the public URL, and delete the local file.

    :param file_path: Path to the file to upload
    :param object_name: S3 object name. If not specified, file_path's basename is used
    :return: Public URL of the uploaded file
    """
    # If S3 object_name was not specified, use file_path's basename
    if object_name is None:
        object_name = os.path.basename(file_path)

    try:
        # Upload the file
        s3.upload_file(file_path, R2_BUCKET_NAME, object_name)
        
        # Generate a public URL for the uploaded file
        url = f"{R2_BASE_URL}/{object_name}"
        
        # Delete the local file
        os.remove(file_path)
        
        return url
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""
    