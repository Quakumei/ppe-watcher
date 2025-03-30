from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, BigInteger, Boolean, Text
from sqlalchemy.orm import relationship
from .database import Base
import enum

# Violation enum
class ViolationType(str, enum.Enum):
    none = "none"
    no_helmet = "no_helmet"
    no_vest = "no_vest"
    no_helmet_no_vest = "no_helmet_no_vest"

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    rtsp_url = Column(String, nullable=False)
    location = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    detection_events = relationship("DetectionEvent", back_populates="camera")


class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"))
    timestamp = Column(BigInteger, nullable=False)
    image_url = Column(String, nullable=False)

    camera = relationship("Camera", back_populates="detection_events")
    person_detections = relationship("PersonDetection", back_populates="event")


class PersonDetection(Base):
    __tablename__ = "person_detections"

    id = Column(Integer, primary_key=True, index=True)
    detection_event_id = Column(Integer, ForeignKey("detection_events.id", ondelete="CASCADE"))
    violation = Column(Enum(ViolationType), nullable=False)
    bbox_x = Column(Float, nullable=False)
    bbox_y = Column(Float, nullable=False)
    bbox_width = Column(Float, nullable=False)
    bbox_height = Column(Float, nullable=False)

    event = relationship("DetectionEvent", back_populates="person_detections")
