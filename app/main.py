from fastapi import FastAPI

from app.database import Base, engine
from app.routes import analytics, auth, habits

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Habit and Productivity Analytics API",
    description="A data-driven API for tracking habits and productivity insights.",
    version="0.1.0",
)

app.include_router(habits.router, prefix="/habits", tags=["Habits"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])


@app.get("/")
def read_root() -> dict:
    return {
        "message": "Habit and Productivity Analytics API is running",
        "version": app.version,
    }
