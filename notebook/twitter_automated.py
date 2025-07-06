import os
import requests
import tweepy
from dotenv import load_dotenv

load_dotenv()

# === 🔧 CONFIGURATION ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# === 🤖 GENERATE TWEET VIA GROQ LLM ===
prompt = (
    "Write a single, short, viral tweet (under 280 characters) "
    "about advanced AI agent infrastructure, LangGraph, LangChain, Groq, MCP Servers, or parallel agent architecture. "
    "Only return the tweet — no thoughts or explanations."
)

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "qwen-qwq-32b",  # Or "mixtral-8x7b-32768" etc.
    "messages": [
        {"role": "system", "content": "You are a viral tech Twitter expert."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.7,
    "max_tokens": 200
}

print("🧠 Sending prompt to Groq...")
llm_response = requests.post(GROQ_API_URL, headers=headers, json=payload)

if llm_response.status_code != 200:
    print(f"❌ LLM generation failed: {llm_response.text}")
    exit()

tweet_text = llm_response.json()["choices"][0]["message"]["content"].strip()
print("✅ Generated Tweet:\n", tweet_text)

# === 🐦 POST TWEET VIA TWITTER API V2 ===
print("📤 Attempting to post tweet to Twitter...")
client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET
)

try:
    response = client.create_tweet(text=tweet_text)
    tweet_id = response.data["id"]
    tweet_url = f"https://twitter.com/blaugrana_rants/status/{tweet_id}"
    print(f"✅ Tweet posted successfully: {tweet_url}")
except Exception as e:
    print(f"❌ Tweet post failed: {str(e)}")
