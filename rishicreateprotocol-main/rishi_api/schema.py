from pydantic import BaseModel
from typing import List, Optional

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
class TrainingRequest(BaseModel):
    file_url: str
    model: str
    webhook: str
    trigger_word: str

class InferenceRequest(BaseModel):
    lora_urls: List[str]
    model: str
    num_images: int
    prompt: str
    webhook: str
