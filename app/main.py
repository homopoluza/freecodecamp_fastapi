import logging
from fastapi import  FastAPI
from contextlib import asynccontextmanager

from .database import init_db, close_db
from .routers import post, user, auth, vote

from fastapi.middleware.cors import CORSMiddleware

# # Detect environment (you can set ENV=production in your shell)
# ENV = os.getenv("ENV", "development")

# if ENV == "production":
#     app = FastAPI(
#         title="Blake Crosley",
#         description="HTMX + FastAPI demo app",
#         version="0.1.0",
#         docs_url=None,          # Disable Swagger UI
#         redoc_url=None,         # Disable ReDoc
#         openapi_url=None,       # Hide /openapi.json
#         default_response_class=ORJSONResponse,
#         contact={"name": "Blake Crosley", "email": "blake@example.com"},
#         license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
#     )
# else:
#     app = FastAPI(
#         title="Blake Crosley",
#         description="HTMX + FastAPI demo app",
#         version="0.1.0",
#         docs_url="/docs",       # Enable Swagger UI
#         redoc_url="/redoc",     # Enable ReDoc
#         openapi_url="/openapi.json",
#         default_response_class=ORJSONResponse,
#         contact={"name": "Blake Crosley", "email": "blake@example.com"},
#         license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
#     )

# # Middleware order matters: last added = first executed
# app.add_middleware(SecurityHeadersMiddleware)
# app.add_middleware(GZipMiddleware, minimum_size=500)
# app.add_middleware(LocaleMiddleware)
# app.add_middleware(RateLimitMiddleware)
# app.add_middleware(SecurityLogMiddleware, site_name="blakecrosley.com")

# Three design decisions matter here. First, docs_url=None and openapi_url=None disable the automatic API documentation endpoints.
#  A public-facing content site does not need /docs or /openapi.json exposed to the internet.8 Second, 
# middleware order matters — security logging executes first (added last) so it captures every request,
#  including those rejected by rate limiting. Third, GZipMiddleware compresses all responses over 500 bytes, which typically reduces HTML transfer size by 70-80%.

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    # await init_db()
    # logger.info("Database connection was successful!")
    yield   
    # Shutdown code (optional)    
    await close_db()  

app = FastAPI(
    lifespan=lifespan,
    title="fastapi-freecodecamp",
    # docs_url=None,     # Disable docs in production
    # redoc_url=None,
    # openapi_url=None,  # Prevent /openapi.json exposure
    )

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
    return {"message": "Hello World"}