from fastapi import APIRouter
from clients.gamma_client import GammaClient

router = APIRouter()

gamma_client = GammaClient()

@router.get("/tags")
async def get_tags():
    """Get resolved tag IDs for locked topics"""
    LOCKED_TOPICS = ["Finance", "Politics", "Technology", "Elections", "Economy"]
    
    topic_labels = [t.lower() for t in LOCKED_TOPICS]
    tag_ids = await gamma_client.resolve_tag_ids(topic_labels)
    
    # Format response
    result = {}
    for label in LOCKED_TOPICS:
        label_lower = label.lower()
        if label_lower in tag_ids:
            result[label] = {
                "id": tag_ids[label_lower],
                "label": label,
            }
    
    return {"tags": result}
