from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

import psutil
import socket
import time
import platform

from minimal_types import Status, GetStatus

APP_NAME = "{{ project_name }}"
PORT = 8000
HOST = f"http://{socket.gethostbyname(socket.gethostname())}"

app = FastAPI()

origins = "{{project.allowed_origins}}"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


@app.get("/status", status_code=status.HTTP_200_OK)
def get_status() -> GetStatus:
    try:
        return GetStatus(
            status=Status.RUNNING,
            app_name=APP_NAME,
            app_version="0.1.0",
            cpu_usage=psutil.cpu_percent(interval=0.1),
            memory_usage=psutil.virtual_memory().percent,
            docs_url=f"{HOST}:{PORT}/docs",
            redoc_url=f"{HOST}:{PORT}/redoc",
        )
    except Exception as e:
        return GetStatus(
            status=Status.ERROR,
            app_name=APP_NAME,
            app_version="0.1.0",
            cpu_usage=0,
            memory_usage=0,
            docs_url=f"{HOST}:{PORT}/docs",
            redoc_url=f"{HOST}:{PORT}/redoc",
            error=str(e),
        )


