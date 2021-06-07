import time
from http.client import HTTPException

import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.middleware.cors import CORSMiddleware

from core.config import *
from routes import student, session, dependencies
from services.oc_api import login_oc

app = FastAPI()
app.include_router(student.router)
app.include_router(session.router)
app.include_router(dependencies.router)

origins = [
    '*'
]


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET,POST"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
