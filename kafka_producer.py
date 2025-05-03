from kafka import KafkaProducer
import json
import time

# Load the emotion mapping (from emotions.json)
with open('emotions.json', 'r') as f:
    emotion_map = json.load(f)

# Convert keys from string to int
emotion_map = {int(k): v for k, v in emotion_map.items()}

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Open the GoEmotions dataset file
with open('train.tsv', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Skip header
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= 2:
        text = parts[0]
        labels = parts[1].split(',')  # Multi-labels possible

        try:
            # Convert label numbers to emotion names
            emotions = [emotion_map[int(label)] for label in labels]
        except KeyError as e:
            print(f"⚠️ Skipping unknown label: {e}")
            continue

        # Final message
        message = {
            'text': text,
            'emotions': emotions  # ✅ Correct key
        }

        producer.send('goemotions', value=message)
        print(f"✅ Sent: {message}")
        time.sleep(1)

producer.flush()
