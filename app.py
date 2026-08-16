import os
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime
from huggingface_hub import InferenceClient
import uuid

# Load .env file
load_dotenv()

# Get token from .env
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Page config
st.set_page_config(
    page_title="Addiction Coach",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .stChatMessage {
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stChatMessage[data-testid="chat-message"][data-role="user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 18px;
    }
    
    .stChatMessage[data-testid="chat-message"][data-role="assistant"] {
        background: white;
        color: #333;
        border-radius: 18px;
        border-left: 4px solid #667eea;
    }
    
        
    .header-container {
        text-align: center;
        color: white;
        padding: 40px 20px 20px;
        max-width: 700px;
        margin: 0 auto;
    }
    
    .header-title {
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-subtitle {
        font-size: 1.1em;
        opacity: 0.95;
        margin-bottom: 20px;
    }
    
    .stChatInputContainer {
        padding: 20px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        margin: 0 auto 20px;
        max-width: 700px;
    }
    
    .stChatInput {
        border-radius: 25px;
        border: 2px solid #667eea;
        padding: 12px 20px;
        font-size: 1em;
    }
    
    .stChatInput:focus {
        border-color: #764ba2;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Message timestamps */
    .stCaption {
        font-size: 0.75em;
        opacity: 0.7;
        margin-top: 4px;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    .viewerBadge_container__r5tak {
        display: none;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2em;
        }
        
        .chat-container,
        .stChatInputContainer {
            margin: 10px;
            max-width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <div class="header-title">🧠 Addiction Coach</div>
    <div class="header-subtitle">A compassionate AI to help when you feel the urge to scroll</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

# System prompt
SYSTEM_PROMPT = """You are a compassionate digital wellness coach. Your tone is calm, empathetic, and never judgmental.

Your job: Help someone who feels the urge to scroll understand WHY they want to scroll, and offer real solutions.

IMPORTANT RULES:
1. Always normalize their urge ("That's real, you're not weak")
2. Ask ONE good question to find the trigger (loneliness? anxiety? boredom?)
3. Listen to their answer carefully
4. Suggest ONE specific tool (not a list)
5. If they mention self-harm or suicide, respond with: "This is serious. Please call 988 (US) or talk to a professional immediately."

WHEN THEY SAY THEY SCROLLED AGAIN:
- Never say "you failed"
- Say: "Okay. No judgment. Let's figure out what triggered it."
- Treat it as information, not failure

START CONVERSATION:
If this is the first message, ask: "Hi. What's going on right now? Do you feel the urge to scroll?"
Then listen and help them understand what they really need."""

# Display chat history (no white container)
for message in st.session_state.messages:
    with st.chat_message(message['role'], avatar="🧠" if message['role'] == "assistant" else "👤"):
        st.write(message['content'])
        st.caption(f"{message['timestamp']}")
# User input
user_input = st.chat_input("Tell me what's on your mind...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now().strftime("%I:%M %p")
    })
    
    # Display user message immediately
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
        st.caption(datetime.now().strftime("%I:%M %p"))
    
    # Call Hugging Face API
    try:
        client = InferenceClient(api_key=HUGGINGFACE_API_KEY)
        
        # Format messages for the API
        messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in st.session_state.messages[:-1]:
            messages_for_api.append({
                "role": msg['role'],
                "content": msg['content']
            })
        messages_for_api.append({
            "role": "user",
            "content": user_input
        })
        
        # Get response from Hugging Face
        response = client.chat_completion(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=messages_for_api,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Add AI response to history
        st.session_state.messages.append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().strftime("%I:%M %p")
        })
        
        # Display AI response
        with st.chat_message("assistant", avatar="🧠"):
            st.write(ai_response)
            st.caption(datetime.now().strftime("%I:%M %p"))
        
        # Rerun to refresh UI
        st.rerun()
    
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Make sure your Hugging Face API token is correct in the .env file.")