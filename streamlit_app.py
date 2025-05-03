# streamlit_app.py

import streamlit as st
from model_handler import predict_emotions
import plotly.express as px

st.set_page_config(page_title="GoEmotions Sentiment Analyzer", layout="centered")

st.title("🎭 Emotion & Sentiment Analyzer")
st.markdown("Enter a sentence with mixed emotions and get detailed analysis!")

# Input
user_input = st.text_area("Type your sentence here:", height=100)

if st.button("Analyze"):
    if user_input.strip() == "":
        st.warning("Please enter a sentence.")
    else:
        sentiment, top_emotions = predict_emotions(user_input)

        # Display sentiment
        st.subheader("🧠 Sentiment")
        st.success(f"**{sentiment}**")

        # Display top emotions with percentages
        st.subheader("🎨 Emotions Detected")
        for emotion, score in top_emotions:
            st.write(f"**{emotion.title()}**: {score:.2f}%")

        # Plot
        st.subheader("📊 Emotion Distribution")
        emotion_labels = [e[0] for e in top_emotions]
        emotion_scores = [e[1] for e in top_emotions]
        fig = px.pie(names=emotion_labels, values=emotion_scores, title="Top Emotions")
        st.plotly_chart(fig)
