import logging
from fastapi import  FastAPI
from contextlib import asynccontextmanager

from .database import init_db, close_db
from .routers import post, user, auth, vote

from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    # await init_db()
    # logger.info("Database connection was successful!")
    yield   
    # Shutdown code (optional)    
    await close_db()  

app = FastAPI(lifespan=lifespan)

origins = ["https://www.google.com"]  # Allow all origins for CORS. In production, you should specify allowed origins for security reasons.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
async def root():
    return {"message": "Hello World!!!"}