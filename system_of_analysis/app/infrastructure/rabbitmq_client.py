import asyncio
import json
from aio_pika import connect_robust, IncomingMessage, ExchangeType
from fastapi import FastAPI
from app.domain.services.usecases import get_application_service
from app.presentation.api.schemas.detection_event_rabbit import DetectionEventRabbit
from sqlalchemy.orm import Session
from app.infrastructure.db.database import SessionLocal

RABBITMQ_URL = "amqp://guest:guest@localhost/"

async def on_message(message: IncomingMessage):
    async with message.process():
        try:
            # Распарсить JSON-сообщение
            payload = json.loads(message.body)
            # Валидация с помощью Pydantic
            detection_msg = DetectionEventRabbit.parse_obj(payload.get("data"))
            # Преобразование данных в доменную модель
            from app.presentation.api.mappers import map_detection_event_in_to_entity
            from app.presentation.api.schemas.detection_event import DetectionEventIn

            # Преобразуем входное сообщение в DetectionEventIn (обратите внимание, что могут потребоваться преобразования – см. ниже)
            event_in_data = {
                "camera_id": detection_msg.cam_id,
                "timestamp": str(detection_msg.timestamp),
                "image_url": detection_msg.image_url,
                "persons": [
                    {
                        "violation": person.violation,
                        "bbox_x": person.bbox_xywh[0],
                        "bbox_y": person.bbox_xywh[1],
                        "bbox_width": person.bbox_xywh[2],
                        "bbox_height": person.bbox_xywh[3],
                    }
                    for person in detection_msg.persons
                ]
            }
            # Создать объект DetectionEventIn
            event_in = DetectionEventIn.parse_obj(event_in_data)

            # Создать сессию БД
            db: Session = next(SessionLocal())
            app_service = get_application_service(db)
            event_entity = map_detection_event_in_to_entity(event_in)
            # Вызываем use-case добавления нарушения
            created_event = app_service.add_detection_event_uc.execute(event_entity)
            print(f"Successfully processed event id={created_event.id}")
        except Exception as e:
            print(f"Error processing message: {e}")


async def start_rabbitmq_listener():
    connection = await connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue("detection_events_queue", durable=True)
    await queue.consume(on_message)
    print(" [*] RabbitMQ listener started")
    return connection  # чтобы можно было закрыть при остановке


def run_rabbitmq_listener_in_background(app: FastAPI):
    loop = asyncio.get_event_loop()
    connection_future = loop.create_task(start_rabbitmq_listener())
    app.state.rabbit_connection = connection_future

    @app.on_event("shutdown")
    async def shutdown_rabbit():
        connection = await app.state.rabbit_connection
        await connection.close()
        print(" [*] RabbitMQ connection closed")
