from fastapi import FastAPI, Request, Query
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.responses import FileResponse
from datetime import datetime
from typing import Optional
import csv

# ✅ Lightweight Emotion Classification Pipeline
classifier = pipeline("text-classification", model="nateraw/bert-base-uncased-emotion", top_k=None)

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Setup ---
DATABASE_URL = "sqlite:///./emotion_history.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analysis"
    id = Column(Integer, primary_key=True, index=True)
    sentence = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    emotions = Column(String)
    sentiment = Column(String)

Base.metadata.create_all(bind=engine)

# --- Input schema ---
class InputText(BaseModel):
    text: str

# --- Predict Endpoint ---
@app.post("/predict")
def predict_emotions(input: InputText):
    result = classifier(input.text)[0]

    total_score = sum([label["score"] for label in result])
    emotions_percent = {
        label["label"]: round((label["score"] / total_score) * 100, 2)
        for label in result if label["score"] > 0.05
    }

    # Sentiment classification
    sentiment = "neutral"
    if "joy" in emotions_percent or "love" in emotions_percent:
        sentiment = "positive"
    elif "anger" in emotions_percent or "sadness" in emotions_percent or "fear" in emotions_percent:
        sentiment = "negative"

    sentiment_scores = {"positive": 0, "negative": 0, "neutral": 0}
    for label in result:
        lbl = label["label"]
        score = label["score"]
        if lbl in ["joy", "love", "amusement", "excitement"]:
            sentiment_scores["positive"] += score
        elif lbl in ["anger", "sadness", "fear", "disappointment", "grief"]:
            sentiment_scores["negative"] += score
        else:
            sentiment_scores["neutral"] += score

    sentiment_percent = {
        k: round((v / sum(sentiment_scores.values())) * 100, 2)
        for k, v in sentiment_scores.items()
    }

    # Save to DB
    db = SessionLocal()
    emotion_labels_str = ", ".join(emotions_percent.keys())
    entry = Analysis(
        sentence=input.text,
        emotions=emotion_labels_str,
        sentiment=sentiment
    )
    db.add(entry)
    db.commit()
    db.close()

    return {
        "sentiment": sentiment,
        "emotions": list(emotions_percent.keys()),
        "percentages": emotions_percent,
        "sentiment_percent": sentiment_percent
    }

# --- History Endpoint ---
@app.get("/history")
def get_history(sentiment: Optional[str] = Query(None)):
    db = SessionLocal()
    query = db.query(Analysis)
    if sentiment:
        query = query.filter(Analysis.sentiment == sentiment.lower())
    records = query.order_by(Analysis.timestamp.desc()).limit(10).all()
    db.close()
    return [
        {
            "sentence": r.sentence,
            "timestamp": r.timestamp,
            "emotions": r.emotions,
            "sentiment": r.sentiment
        } for r in records
    ]

# --- Export CSV Endpoint ---
@app.get("/export")
def export_history():
    db = SessionLocal()
    records = db.query(Analysis).all()
    db.close()

    file_path = "history_export.csv"
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Sentence", "Timestamp", "Emotions", "Sentiment"])
        for r in records:
            writer.writerow([r.id, r.sentence, r.timestamp, r.emotions, r.sentiment])

    return FileResponse(path=file_path, filename="emotion_analysis_history.csv", media_type='text/csv')
