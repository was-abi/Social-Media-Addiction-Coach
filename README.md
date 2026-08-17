# 🧠 Addiction Coach

**An AI behavioral coach helping you break free from short-form video scroll addiction using Cognitive Behavioral Therapy techniques.**

---

## Overview

Addiction Coach is a free, open-source AI chatbot built with Streamlit and Hugging Face that helps people struggling with smartphone addiction—specifically short-form video content addiction (Instagram Reels, YouTube Shorts, TikTok).

The coach uses CBT (Cognitive Behavioral Therapy) techniques to help users identify triggers behind their scrolling urges and offer personalized coping strategies without judgment. Unlike generic "just delete the app" advice, this tool addresses the *root cause* of the addiction.

**Who is this for?**
- People who experience compulsive scrolling urges
- Anyone who loses hours to short-form video feeds without realizing it
- Those who feel shame or guilt about their scroll habits (this tool normalizes the struggle)

---

## Why This Project Matters

### The Problem

Research shows that users don't struggle with "social media addiction" broadly—they're addicted to *short-form video feeds specifically*. Common pain points include:

- **Compulsive autopilot scrolling** — watching content you don't even care about
- **Extreme time loss** — 7+ hour sessions that pass unnoticed
- **Shame spirals** — feeling weak or lazy, not understanding the real issue
- **Loneliness compensation** — scrolling fills the social void when you're alone
- **Dopamine dysregulation** — can't enjoy normal activities anymore
- **Anxiety avoidance** — scrolling numbs uncomfortable feelings instead of solving them

**Why existing solutions fail:**
- Deleting the app = treating the symptom, not the disease
- Screen time limits = users just scroll more efficiently (or guilt spiral)
- Willpower-based approaches = unsustainable without understanding triggers

### Our Approach

Addiction Coach takes a different path:

1. **Identifies real triggers** — loneliness, anxiety, boredom, procrastination, or emotional avoidance
2. **Offers specific tools** — not generic advice, but actionable alternatives (call someone, journal, go for a walk, breathing exercise)
3. **Manages shame** — treats relapse as *data*, not failure ("What did this tell us about your trigger?")
4. **Stays empathetic** — calm, non-judgmental tone throughout
5. **Fully free** — no paywalls, no tracking, no data collection

---

## How It Works

```
User message → Streamlit UI
        ↓
System prompt enforces CBT structure (one question at a time)
        ↓
Llama 3.1 8B (via Hugging Face) generates coached response
        ↓
Safety check: detect crisis language → redirect to 988 if needed
        ↓
Response displayed in real-time chat
```

The app maintains a chat history per session. Each AI response follows a strict pattern:
1. Normalize the urge ("That's real, you're not weak")
2. Ask *one* good question to find the trigger
3. Listen to the answer
4. Suggest *one* specific tool (not a list)
5. If crisis language detected → immediate redirect to 988 (US) or professional support

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit (simple, no frontend setup needed) |
| **LLM** | Hugging Face Inference API (free tier) |
| **Model** | Llama 3.1 8B Instruct |
| **Deployment** | Streamlit Community Cloud (free) |
| **Language** | Python 3.13+ |
| **Package Manager** | `uv` (or `pip` fallback) |

---

## Getting Started

### Prerequisites

- **Python 3.13+** ([download](https://www.python.org/downloads/) or use `pyenv`/`uv`)
- **Free Hugging Face account** ([signup](https://huggingface.co/join))
- **Git** (to clone the repo)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/scroll-coach.git
cd scroll-coach
```

### Step 2: Get a Hugging Face API Token

1. Go to [huggingface.co](https://huggingface.co)
2. Click your profile → **Settings** → **Access Tokens**
3. Click "New token" → name it `scroll-coach`
4. Set permission to **Read** (not Write)
5. Copy the token (starts with `hf_`)

⚠️ **Important:** Never commit this token to git. The `.gitignore` already excludes `.env`, so keep the token *only* in your local `.env` file.

### Step 3: Create a `.env` File

In the project root, create a `.env` file:

```bash
# .env
HUGGINGFACE_API_KEY=your_hf_token_here
```

Replace `your_hf_token_here` with your actual token from Step 2.

### Step 4: Install Dependencies

**Option A: Using `uv` (recommended)**

```bash
uv sync
```

**Option B: Using `pip`**

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### Step 5: Run the App

```bash
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`). Open it in your browser.

### Step 6: Start Coaching

Type a message to the coach. Try something like:
- "I feel the urge to scroll right now"
- "I just scrolled for 3 hours and I hate myself"
- "I'm bored and want to watch Reels"

---

## Deploying to Streamlit Cloud (Free)

### Prerequisites

- Code pushed to a public GitHub repo
- Hugging Face API token ready

### Deploy Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add app"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repo and `app.py` as the main file

3. **Add the Hugging Face API Key as a Secret**
   - In the app settings (gear icon → "Settings" → "Secrets")
   - Add:
     ```
     HUGGINGFACE_API_KEY = "your_hf_token_here"
     ```

4. **Deploy**
   - Click "Deploy"
   - Streamlit will build and host your app (live in ~2 minutes)

Your app is now live and shareable!

---

## Project Structure

```
scroll-coach/
├── app.py                 # Main Streamlit app
├── pyproject.toml         # Project metadata & dependencies (uv)
├── requirements.txt       # Dependencies for pip
├── .env                   # API keys (gitignored, never commit)
├── .gitignore             # Ignores .env, .venv, etc.
├── README.md              # This file
└── .python-version        # Python 3.13
```

---

## Safety Note

⚠️ **This tool is not a substitute for professional mental health care.**

Addiction Coach uses AI to offer supportive dialogue based on CBT principles. It is designed to:
- Help you understand your triggers
- Suggest healthy coping strategies
- Normalize your experience

It is **not** designed to:
- Replace therapy or counseling
- Handle crisis situations (though it tries to detect and redirect them)
- Diagnose mental health conditions

**If you or someone you know is in crisis:**
- **US:** Call or text 988 (Suicide & Crisis Lifeline)
- **International:** Visit [findahelpline.com](https://findahelpline.com)
- **Always consider talking to a doctor or therapist about underlying anxiety, depression, or loneliness.**

---

## Security Note

### API Key Safety

The `.env` file in your local repository contains your Hugging Face API key. This file is gitignored and should *never* be committed to version control.

**If your API key was ever shared or accidentally committed:**

1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Delete the compromised token immediately
3. Create a new token and update your `.env` file

Treat your API key like a password—if it's exposed, anyone can use your Hugging Face quota.

---

## Contributing

Contributions welcome! This is an open-source project, and we'd love help with:

- Improving the CBT prompt structure
- Adding new coping strategy suggestions
- Testing on different deployment platforms
- Bug fixes and performance improvements
- Better crisis-language detection

Feel free to open an issue or submit a pull request.

---

## License

This project is open-source. See LICENSE file for details (if you'd like to add a specific license, MIT is recommended).

---

## Questions?

- **How does the free tier work?** Hugging Face Inference API is free up to a certain usage limit. For high-traffic deployments, you may need to upgrade.
- **Can I self-host this?** Yes! You can replace the HF Inference client with any LLM endpoint (Ollama, vLLM, local models, etc.).
- **Does this collect my data?** No. Your messages are stored in browser session state only. They're not sent to any server except Hugging Face (which follows their privacy policy).
- **Can I use a different LLM?** Yes, modify the `InferenceClient` call in `app.py` to use any compatible API.

## Watch the Build

**[Watch the full development walkthrough on YouTube](https://www.youtube.com/watch?v=UUxKlsmmVE0)** — See how this project was built from scratch.

---

**Built with ❤️ to help you scroll less and live more.**
