from fastapi import FastAPI, Depends
from dotenv import load_dotenv
# load env vars (for DB URL, etc.)
load_dotenv()

# import DB setup
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db

# import lookup routers
from app.routers.lookups import router as lookups_router
from app.routers.classifications import router as classifications_router
from app.routers.varietals import router as varietals_router
from app.routers.wines import router as wines_router
from app.routers.purchases import router as purchases_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    # Create the database tables if they do not exist
    Base.metadata.create_all(bind=engine)

app.include_router(lookups_router)
app.include_router(classifications_router)
app.include_router(varietals_router)
app.include_router(wines_router)
app.include_router(purchases_router)

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/health/db")
def health_check(db: Session = Depends(get_db)):
    result = db.execute("SELECT 1").scalar()
    return {"db_connected": result == 1}