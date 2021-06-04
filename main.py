import uvicorn
from fastapi import FastAPI


from core.config import *
from routes import student, session

app = FastAPI()
app.include_router(student.router)
app.include_router(session.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
