from fastapi import FastAPI

from crud import router
from core.db import Base, engine
from backend_pre_start import *
from fastapi_utils.timing import add_timing_middleware

app = FastAPI()
app.include_router(router)
add_timing_middleware(app, record=logger.info)

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(app, host="0.0.0.0", port = 3045)
