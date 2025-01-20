from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Client as DBClient, Base
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Set up SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# FastAPI instance
app = FastAPI()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class ClientCreate(BaseModel):
    name: str
    email: str
    address: str

class Client(ClientCreate):
    id: int

    class Config:
        orm_mode = True

# Routes

# Create a new client
@app.post("/clients/", response_model=Client)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = db.query(DBClient).filter(DBClient.email == client.email).first()
    if db_client:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_client = DBClient(name=client.name, email=client.email, address=client.address)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# Get all clients
@app.get("/clients/", response_model=List[Client])
def get_clients(db: Session = Depends(get_db)):
    clients = db.query(DBClient).all()
    return clients