from fastapi import APIRouter, Response
import requests

router = APIRouter()

@router.get("/proxy-image")
def proxy_image(url: str):
    resp = requests.get(url)
    return Response(content=resp.content, media_type="image/jpeg")
