from sqlalchemy import create_engine, Column, Integer, String, Boolean, JSON
from database import Base

# Database models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    status = Column(String)
    job_type = Column(String)  # 'training' or 'inference'
    model = Column(String)
    webhook = Column(String)
    meta_data = Column(String)
    output = Column(String)
