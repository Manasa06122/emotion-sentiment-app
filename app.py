import streamlit as st
import requests
import plotly.express as px

st.set_page_config(page_title="Emotion & Sentiment Analyzer", layout="centered")
st.title("🧠 Sentiment & Emotion Analyzer")

text = st.text_area("Enter your sentence:")

# Analyze
if st.button("Analyze"):
    with st.spinner("Analyzing..."):
        try:
            res = requests.post("http://127.0.0.1:8000/predict", json={"text": text})
            data = res.json()

            st.markdown(f"❤️ **Predicted Sentiment:** `{data['sentiment'].capitalize()}`")

            st.markdown("🎭 **Emotions Detected:**")
            for emo in data["emotions"]:
                st.write(f"- {emo}")

            st.markdown("📈 **Emotion Percentages:**")
            fig1 = px.pie(
                names=list(data["percentages"].keys()),
                values=list(data["percentages"].values()),
                title="Emotion Distribution"
            )
            st.plotly_chart(fig1)

            st.markdown("📊 **Sentiment Percentages:**")
            sentiment_percent = data.get("sentiment_percent", {})
            fig2 = px.pie(
                names=list(sentiment_percent.keys()),
                values=list(sentiment_percent.values()),
                title="Sentiment Breakdown"
            )
            st.plotly_chart(fig2)

        except Exception as e:
            st.error(f"Error: {e}")

# ------------------------
# History & Export Section
# ------------------------
st.markdown("---")
st.subheader("📜 View History")

sentiment_filter = st.selectbox("Filter by Sentiment", options=["All", "Positive", "Negative", "Neutral"])

if st.button("Fetch History"):
    with st.spinner("Fetching history..."):
        try:
            params = {}
            if sentiment_filter != "All":
                params["sentiment"] = sentiment_filter.lower()
            res = requests.get("http://127.0.0.1:8000/history", params=params)
            history = res.json()

            if history:
                for item in history:
                    st.write(f"📝 `{item['sentence']}`")
                    st.write(f"📅 {item['timestamp']}")
                    st.write(f"🎭 Emotions: `{item['emotions']}`")
                    st.write(f"❤️ Sentiment: `{item['sentiment'].capitalize()}`")
                    st.markdown("---")
            else:
                st.info("No matching records found.")

        except Exception as e:
            st.error(f"Error fetching history: {e}")

# Export Button
if st.button("📤 Export All History to CSV"):
    try:
        export_url = "http://127.0.0.1:8000/export"
        st.success(f"[Click here to download CSV]({export_url})", icon="📁")
    except Exception as e:
        st.error(f"Error exporting CSV: {e}")
