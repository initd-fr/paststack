from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

import psutil
import time
import platform

from minimal_types import Status, GetStatus


app = FastAPI()


@app.get("/status", status_code=status.HTTP_200_OK)
def get_status() -> GetStatus:

    

