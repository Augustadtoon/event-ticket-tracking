from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

from app.db.database import Base, engine 
from app.api import auth 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine) 

app.include_router(auth.router, prefix="/auth") 

@app.get("/") 
def home(): 
    return {"message:": "Auth system ready" }