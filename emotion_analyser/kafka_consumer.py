from kafka import KafkaConsumer
import json

# Load label-to-emotion mapping (optional for your use case)
with open("emotions.json", "r") as f:
    emotion_map = json.load(f)

# Load emotion-to-sentiment mapping
with open("sentiment_dict.json", "r") as f:
    sentiment_dict = json.load(f)

# Kafka Consumer
consumer = KafkaConsumer(
    'goemotions',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='emotion-consumer',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("🔍 Listening for Kafka messages...\n")

for message in consumer:
    data = message.value
    print(f"📦 Received message: {data}")

    # Extract text and emotion(s)
    text = data.get("text", "")
    emotions = data.get("emotions", [])

    # Default values
    predicted_emotion = "neutral"
    sentiment = "neutral"

    # Pick the first valid emotion from the list (if any)
    if emotions:
        predicted_emotion = emotions[0]

        # Look up sentiment
        for sent_type, sent_emotions in sentiment_dict.items():
            if predicted_emotion in sent_emotions:
                sentiment = sent_type
                break

    print(f"\n📝 Text: {text}")
    print(f"🎭 Emotion: {predicted_emotion}")
    print(f"❤️ Sentiment: {sentiment}")

    # Save for frontend
    result = {
        "text": text,
        "predicted_emotion": predicted_emotion,
        "predicted_sentiment": sentiment
    }

    with open("result.json", "w") as f:
        json.dump(result, f, indent=2)

    input("\n🔁 Press Enter to see the next prediction...\n")
