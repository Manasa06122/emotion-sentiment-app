# train_model.py

import pandas as pd
import json
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer

# Load dataset
df = pd.read_csv("goemotions_merged.csv")  # your dataset
df = df[['text', 'labels']]  # Ensure only required columns

# Load emotions mapping
with open("emotions.json") as f:
    emotions = json.load(f)

# Prepare labels
df['labels'] = df['labels'].apply(eval)  # convert string list to actual list
mlb = MultiLabelBinarizer()
Y = mlb.fit_transform(df['labels'])

# TF-IDF vectorizer
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df['text'])

# Train/test split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, Y_train)

# Save models
joblib.dump(model, "emotion_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")
joblib.dump(mlb, "mlb.pkl")

print("✅ Model training complete and saved!")
