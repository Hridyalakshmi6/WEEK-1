import streamlit as st
import pandas as pd
import time
from dotenv import load_dotenv
import google.generativeai as genai
import os
import re

# -------------------------
# Load API Key
# -------------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ GOOGLE_API_KEY not found in .env file")
else:
    genai.configure(api_key=api_key)

# -------------------------
# Load CSV
# -------------------------
data = pd.read_csv("cleaned_ev_charging_patterns.csv")
st.title("Chatbot for Electric Vehicles clarifications")

columns_list = data.columns.tolist()
selected_topic = st.selectbox("Select a topic from CSV:", columns_list)

time.sleep(1)
st.write("You selected:", selected_topic)

# -------------------------
# Chat history
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Ask me anything about Electric Vehicles."}
    ]

# Display history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# -------------------------
# Function: Keyword-based CSV search
# -------------------------
def search_csv(query):
    keywords = re.findall(r"\w+", query.lower())

    # combine all rows containing ANY keyword
    mask = False
    for kw in keywords:
        mask |= data.apply(lambda row: row.astype(str).str.contains(kw, case=False).any(), axis=1)

    matched_rows = data[mask]

    # limit results to avoid overloading the prompt
    return matched_rows.head(5)

# -------------------------
# User Input
# -------------------------
user_input = st.chat_input("Ask your EV question:")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    # CSV search
    matched = search_csv(user_input)

    # Create contextual info
    context_text = matched.to_string(index=False) if not matched.empty else "No relevant CSV data found."

    # -------------------------
    # Create prompt
    # -------------------------
    prompt = f"""
You are an EV expert. Use the CSV information only if relevant.

CSV context:
{context_text}

Selected column: {selected_topic}

User question:
{user_input}

If CSV does not help, answer normally.
"""

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        reply = model.generate_content(prompt).text
    except:
        reply = "❌ Error: Could not connect to Gemini."

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").markdown(reply)
