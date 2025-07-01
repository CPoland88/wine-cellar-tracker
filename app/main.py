from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal

app = FastAPI()

@app.on_event("startup")
def on_startup():
    # Create the database tables if they do not exist
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/health/db")
def health_check(db: Session = Depends(get_db)):
    result = db.execute("SELECT 1").scalar()
    return {"db_connected": result == 1}