import time

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import dependencies, invoice, session, student, utils
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# INCLUDES ROUTES
app.include_router(student.router)
app.include_router(session.router)
app.include_router(invoice.router)
app.include_router(dependencies.router)
# app.include_router(utils.router)

# INCLUDES DEV DEPENDCIES
if settings.DEV:
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


# INCLUDE MIDDLEWARES
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET,POST,PUT,DELETE"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVER_PORT, reload=True)
