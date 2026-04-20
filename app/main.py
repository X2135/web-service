from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.routes import analytics, auth, habits

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Habit and Productivity Analytics API",
    description="A data-driven API for tracking habits and productivity insights.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(habits.router, prefix="/habits", tags=["Habits"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])


def _default_error_code(status_code: int) -> str:
    mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
    }
    return mapping.get(status_code, "HTTP_ERROR")


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    # Keep a stable error contract so clients can always read `detail` and `code`.
    if isinstance(exc.detail, dict):
        detail = exc.detail.get("detail", "Request failed.")
        code = exc.detail.get("code", _default_error_code(exc.status_code))
    else:
        detail = str(exc.detail)
        code = _default_error_code(exc.status_code)

    return JSONResponse(status_code=exc.status_code, content={"detail": detail, "code": code})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else {"msg": "Invalid request payload."}
    return JSONResponse(
        status_code=422,
        content={
            "detail": first_error.get("msg", "Invalid request payload."),
            "code": "VALIDATION_ERROR",
        },
    )


@app.get("/")
def read_root() -> dict:
    return {
        "message": "Habit and Productivity Analytics API is running",
        "version": app.version,
    }
