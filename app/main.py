import logging
from fastapi import  FastAPI
from contextlib import asynccontextmanager

from .database import init_db, close_db
from .routers import post, user, auth

logger = logging.getLogger("uvicorn.error")



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await init_db()
    logger.info("Database connection was successful!")
    yield   
    # Shutdown code (optional)    
    await close_db()  

app = FastAPI(lifespan=lifespan)        


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Hello World!!!"}