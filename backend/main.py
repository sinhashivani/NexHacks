from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from routers import recommendations, tags
from database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Polymarket Trade Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations.router, prefix="/v1", tags=["recommendations"])
app.include_router(tags.router, prefix="/v1", tags=["tags"])

@app.get("/")
async def root():
    return {"message": "Polymarket Trade Assistant API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
