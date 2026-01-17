from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from Polymarket_API.get_markets_data import ui
from Polymarket_API.get_similar_markets import get_similar_by_event_title

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

@app.get("/similar")
def get_similar(
    event_title: str = Query(..., description="Exact market question title")
):
    try:
        data = get_similar_by_event_title(event_title)
        if not data:
            raise HTTPException(status_code=404, detail="Event not found")
        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))