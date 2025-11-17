import streamlit as st
import random
import textwrap
import os

# Optional OpenAI import
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(
    page_title="Role-based Creative Chatbot",
    page_icon="🎭",
    layout="wide"
)

st.title("🎭 Role-based Creative Chatbot")
st.caption("An intelligent story generator powered by OpenAI (with offline fallback).")

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.header("⚙️ Chatbot Settings")

role = st.sidebar.selectbox(
    "Choose a Role",
    [
        "Storyteller",
        "Poet",
        "Screenwriter",
        "Sci-Fi Author",
        "Comedian",
        "Motivational Coach",
        "Marketing Strategist",
        "Game Designer",
    ],
    index=0
)

tone = st.sidebar.selectbox(
    "Tone",
    ["Neutral", "Friendly", "Inspirational", "Formal", "Playful"],
    index=2
)

length = st.sidebar.selectbox("Response Length", ["Short", "Medium", "Long"], index=1)

creativity = st.sidebar.slider("Creativity Level", 0.0, 1.0, 0.7, 0.05)

style = st.sidebar.multiselect(
    "Writing Devices",
    ["Metaphor", "Alliteration", "Rule of Three", "Rhetorical Question", "Sensory Detail"],
    default=["Metaphor"]
)

st.sidebar.markdown("---")
st.sidebar.info("Adjust style and tone, then type your prompt below!")

# ---------------------------
# API Key Setup
# ---------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))

# Initialize client if key exists
client = None
if OPENAI_API_KEY and OpenAI:
    client = OpenAI(api_key=OPENAI_API_KEY)
    st.sidebar.success("✅ OpenAI API key detected — online mode enabled.")
else:
    st.sidebar.warning("⚠️ No API key found — running in offline demo mode.")

# ---------------------------
# Helper Functions
# ---------------------------
def stylize_text(text: str) -> str:
    """Apply creative writing devices for stylistic variation."""
    if "Metaphor" in style and random.random() < creativity:
        text += " It’s like painting with light and shadow."
    if "Alliteration" in style and random.random() < creativity:
        text = text.replace("strong", "swift and steady")
    if "Rule of Three" in style and random.random() < creativity:
        text += " Balance, rhythm, and resonance."
    if "Rhetorical Question" in style and random.random() < creativity:
        text += " What could be more inspiring?"
    if "Sensory Detail" in style and random.random() < creativity:
        text += " You can almost feel the warmth in every word."
    return text


def generate_story_with_api(role, tone, text, creativity, length):
    """Generate story using OpenAI API"""
    if not text.strip():
        return "Please enter a prompt."

    prompt = (
        f"You are a {role} writing in a {tone.lower()} tone. "
        f"Write a complete {length.lower()} story based on the prompt below.\n\n"
        f"Prompt: {text}\n\n"
        f"Use vivid language, imagination, and emotional flow."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=creativity,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ API Error: {e}"


def generate_story_offline(role, tone, text, creativity, length):
    """Offline fallback generator"""
    if not text.strip():
        return "Please enter a prompt to start."

    intro = f"From a {role.lower()}'s perspective, here's a story about {text.lower()}:"
    parts = [
        "Once upon a time, there was a spark of hope that refused to fade.",
        "In the quiet corners of the city, whispers of change began to rise.",
        "The journey was long, but every challenge revealed new strength.",
        "By the end, what seemed impossible became a story worth remembering."
    ]
    k = {"Short": 1, "Medium": 2, "Long": 4}[length]
    body = "\n\n".join(random.sample(parts, k=k))
    styled = stylize_text(body)
    return f"{intro}\n\n{styled}\n\n(Written in a {tone.lower()} tone.)"


def generate_response(role, tone, text, creativity, length):
    """Auto-select online/offline generation"""
    if client:
        return generate_story_with_api(role, tone, text, creativity, length)
    else:
        return generate_story_offline(role, tone, text, creativity, length)


# ---------------------------
# User Input
# ---------------------------
st.markdown("### 💬 Enter your Prompt")
prompt = st.text_area(
    "What would you like me to write about?",
    placeholder="e.g. A story about two explorers on Mars",
    height=150
)

if st.button("✨ Generate Story", type="primary", use_container_width=True):
    st.subheader(f"🧠 {role}'s Response")
    story = generate_response(role, tone, prompt, creativity, length)
    st.write(story)

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.caption(
    "Powered by Streamlit + OpenAI API. If no API key is set, the app will switch to offline demo mode automatically."
)
