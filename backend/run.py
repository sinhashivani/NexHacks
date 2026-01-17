import uvicorn

if __name__ == "__main__":
    # Start server (lifespan handlers in main.py handle DB connection)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
