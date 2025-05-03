from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    sentiment = Column(String)
    emotions = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
