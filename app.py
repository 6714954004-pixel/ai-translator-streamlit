import streamlit as st
import anthropic
import os

st.set_page_config(
    page_title="LinguaAI Translator",
    page_icon="🌐",
    layout="centered"
)

# --- Styling ---
st.markdown("""
<style>
    .main { max-width: 750px; }
    .result-box {
        background: #1e1e2e;
        border-left: 4px solid #7c6af7;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
        font-size: 1.1rem;
        line-height: 1.7;
        color: #e0e0f0;
    }
    .detected-tag {
        display: inline-block;
        background: rgba(124,106,247,0.15);
        border: 1px solid rgba(124,106,247,0.4);
        color: #9b8cf8;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        margin-bottom: 0.8rem;
    }
    .stTextArea textarea {
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🌐 LinguaAI Translator")
st.write("แปลภาษาด้วย Claude AI · รองรับ 10+ ภาษา · Auto-detect ภาษาต้นทาง")
st.divider()

# --- Language options ---
LANGUAGES = {
    "🔍 Auto Detect": "auto",
    "🇹🇭 Thai (ภาษาไทย)": "th",
    "🇺🇸 English": "en",
    "🇨🇳 Chinese (中文)": "zh",
    "🇯🇵 Japanese (日本語)": "ja",
    "🇰🇷 Korean (한국어)": "ko",
    "🇫🇷 French (Français)": "fr",
    "🇩🇪 German (Deutsch)": "de",
    "🇪🇸 Spanish (Español)": "es",
    "🇸🇦 Arabic (العربية)": "ar",
    "🇻🇳 Vietnamese (Tiếng Việt)": "vi",
}
LANG_NAMES = {v: k for k, v in LANGUAGES.items()}

# --- Input UI ---
col1, col2, col3 = st.columns([5, 1, 5])

with col1:
    source_label = st.selectbox("ภาษาต้นทาง", list(LANGUAGES.keys()), index=0)

with col2:
    st.markdown("<div style='text-align:center;padding-top:30px;font-size:1.4rem;color:#7c6af7'>⇄</div>", unsafe_allow_html=True)

with col3:
    target_options = [k for k in LANGUAGES.keys() if k != "🔍 Auto Detect"]
    default_target = target_options.index("🇺🇸 English") if source_label != "🇺🇸 English" else target_options.index("🇹🇭 Thai (ภาษาไทย)")
    target_label = st.selectbox("ภาษาปลายทาง", target_options, index=default_target)

st.markdown("")

text_input = st.text_area(
    "✏️ ข้อความที่ต้องการแปล:",
    height=160,
    placeholder="พิมพ์หรือวางข้อความที่นี่...",
    max_chars=2000
)

char_count = len(text_input)
st.caption(f"{char_count} / 2000 ตัวอักษร")

# --- Translate Button ---
if st.button("✨ แปลภาษา", use_container_width=True, type="primary"):
    if not text_input.strip():
        st.warning("⚠️ กรุณาพิมพ์ข้อความก่อนกด แปลภาษา")
    else:
        source_code = LANGUAGES[source_label]
        target_code = LANGUAGES[target_label]

        if source_code != "auto" and source_code == target_code:
            st.warning("⚠️ ภาษาต้นทางและปลายทางต้องไม่เหมือนกัน")
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                st.error("❌ ไม่พบ ANTHROPIC_API_KEY — กรุณาตั้งค่า Environment Variable")
                st.stop()

            target_name = target_label.split(" ", 1)[1]  # strip emoji

            if source_code == "auto":
                prompt = f"""Detect the language of the following text, then translate it to {target_name}.

Text: {text_input}

Reply ONLY in this JSON format, no markdown, no extra text:
{{"detected_language": "<language name in English>", "translated": "<translated text>"}}"""
            else:
                source_name = source_label.split(" ", 1)[1]
                prompt = f"""Translate the following text from {source_name} to {target_name}.

Text: {text_input}

Reply ONLY in this JSON format, no markdown, no extra text:
{{"translated": "<translated text>"}}"""

            with st.spinner("🤖 Claude กำลังแปล..."):
                try:
                    import json
                    client = anthropic.Anthropic(api_key=api_key)
                    message = client.messages.create(
                        model="claude-opus-4-5",
                        max_tokens=1024,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    raw = message.content[0].text.strip()
                    result = json.loads(raw)

                    st.divider()
                    st.subheader("📋 ผลการแปล")

                    if result.get("detected_language"):
                        st.markdown(f'<div class="detected-tag">🔍 ตรวจพบภาษา: {result["detected_language"]}</div>', unsafe_allow_html=True)

                    st.markdown(f'<div class="result-box">{result["translated"]}</div>', unsafe_allow_html=True)

                    st.markdown("")
                    st.code(result["translated"], language=None)
                    st.caption("👆 คลิกที่กล่องด้านบนเพื่อ copy ข้อความ")

                    # Save history in session
                    if "history" not in st.session_state:
                        st.session_state.history = []
                    st.session_state.history.insert(0, {
                        "original": text_input[:80] + ("..." if len(text_input) > 80 else ""),
                        "translated": result["translated"][:80] + ("..." if len(result["translated"]) > 80 else ""),
                        "from": result.get("detected_language") or source_label,
                        "to": target_label,
                    })
                    if len(st.session_state.history) > 5:
                        st.session_state.history.pop()

                except json.JSONDecodeError:
                    st.error("❌ ไม่สามารถอ่านผลลัพธ์จาก AI ได้ ลองใหม่อีกครั้ง")
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")

# --- History ---
if "history" in st.session_state and st.session_state.history:
    st.divider()
    st.subheader("📜 ประวัติการแปลล่าสุด")
    for i, item in enumerate(st.session_state.history):
        with st.expander(f"🔹 {item['original']}", expanded=False):
            st.write(f"**แปลจาก:** {item['from']}  →  **{item['to']}**")
            st.write(f"**ผลลัพธ์:** {item['translated']}")

st.divider()
st.caption("Built with ❤️ using Streamlit + Claude AI · LinguaAI v1.0")
