# 🌐 LinguaAI Translator

AI-powered translator app built with **Streamlit** + **Claude AI** — supports 10+ languages with auto language detection.

## Features
- 🔍 Auto language detection
- 🌍 10+ languages (TH, EN, ZH, JA, KO, FR, DE, ES, AR, VI)
- ⚡ Powered by Claude claude-opus-4-5
- 📜 Translation history (session)
- 🐳 Docker ready

## Local Development

```bash
# 1. Clone repo
git clone <your-repo-url>
cd ai-translator-streamlit

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
export ANTHROPIC_API_KEY=your_key_here

# 4. Run app
streamlit run app.py
# Open: http://localhost:8501
```

## Deploy on Render

1. Push repo to GitHub
2. Render → New → **Web Service**
3. Connect repo, set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
4. Add env var: `ANTHROPIC_API_KEY = sk-ant-...`
5. Deploy 🚀

## Docker

```bash
docker build -t linguaai .
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=your_key linguaai
```
