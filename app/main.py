from fastapi import FastAPI, Depends
from dotenv import load_dotenv
# load env vars (for DB URL, etc.)
load_dotenv()

# import DB setup
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db

# import lookup router
from app.routers.lookups import router as lookups_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    # Create the database tables if they do not exist
    Base.metadata.create_all(bind=engine)

app.include_router(lookups_router)

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/health/db")
def health_check(db: Session = Depends(get_db)):
    result = db.execute("SELECT 1").scalar()
    return {"db_connected": result == 1}