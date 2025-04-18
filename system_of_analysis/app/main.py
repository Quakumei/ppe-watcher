import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.infrastructure.db.database import init_db
from app.presentation.api import cameras, detection_events, proxy
from app.infrastructure.rabbitmq_client import run_rabbitmq_listener_in_background

app = FastAPI(title="PPE Safety Monitoring API", version="1.0.0")


@app.on_event("startup")
def on_startup():
    init_db()
    # Запускаем RabbitMQ подписчика
    run_rabbitmq_listener_in_background(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],  # Или ["*"] — на время разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["Cameras"])
app.include_router(detection_events.router, prefix="/api/v1/detections", tags=["Detection Events"])
app.include_router(proxy.router, prefix="/api/v1", tags=["Proxy"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
