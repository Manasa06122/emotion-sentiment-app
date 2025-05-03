# model_handler.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Load the public model
model_name = "nateraw/bert-base-uncased-go-emotions"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Labels from GoEmotions
labels = [
    'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring',
    'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval',
    'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief',
    'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization',
    'relief', 'remorse', 'sadness', 'surprise', 'neutral'
]

def predict_emotions(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = F.sigmoid(logits).squeeze().cpu().numpy()

    # Convert to emotion percentages
    emotion_scores = {label: float(probs[i]) * 100 for i, label in enumerate(labels)}
    sorted_emotions = dict(sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True))

    # Sentiment based on dominant emotions
    top_emotions = list(sorted_emotions.items())[:5]
    sentiment = classify_sentiment(top_emotions)

    return sentiment, top_emotions

def classify_sentiment(top_emotions):
    positive = {'joy', 'love', 'gratitude', 'admiration', 'approval', 'excitement', 'relief', 'pride', 'amusement', 'optimism'}
    negative = {'anger', 'annoyance', 'disgust', 'sadness', 'fear', 'grief', 'remorse', 'disappointment'}
    
    pos_score = sum(score for emotion, score in top_emotions if emotion in positive)
    neg_score = sum(score for emotion, score in top_emotions if emotion in negative)

    if pos_score > neg_score:
        return "Positive"
    elif neg_score > pos_score:
        return "Negative"
    else:
        return "Neutral"
