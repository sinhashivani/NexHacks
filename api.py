from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from Polymarket_API.get_markets_data import ui

app = FastAPI(
    title="Polymarket UI Service",
    version="1.0.0",
)

@app.get("/ui")
def get_ui(token_id: str = Query(..., description="CLOB token id")):
    try:
        data = ui(token_id.strip())
        if not data:
            raise HTTPException(status_code=404, detail="Market not found")
        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

