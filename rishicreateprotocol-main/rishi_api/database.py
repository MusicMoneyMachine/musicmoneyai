from sqlalchemy import create_engine, Column, Integer, String, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from constants import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=10,max_overflow=2,pool_recycle=300,pool_pre_ping=True,pool_use_lifo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
