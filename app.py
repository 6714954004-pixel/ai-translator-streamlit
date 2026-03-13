import streamlit as st
import anthropic
import json
import os

st.set_page_config(
    page_title="LinguaAI Translator",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 LinguaAI Translator")
st.caption("แปลภาษาด้วย Claude AI · รองรับ 10+ ภาษา · Auto-detect ภาษาต้นทาง")
st.divider()

LANGUAGES = {
    "🔍 Auto Detect": "auto",
    "🇹🇭 Thai": "th",
    "🇺🇸 English": "en",
    "🇨🇳 Chinese": "zh",
    "🇯🇵 Japanese": "ja",
    "🇰🇷 Korean": "ko",
    "🇫🇷 French": "fr",
    "🇩🇪 German": "de",
    "🇪🇸 Spanish": "es",
    "🇸🇦 Arabic": "ar",
    "🇻🇳 Vietnamese": "vi",
}

col1, col2, col3 = st.columns([5, 1, 5])

with col1:
    source_label = st.selectbox("ภาษาต้นทาง", list(LANGUAGES.keys()), index=0)

with col2:
    st.write("")
    st.write("")
    st.write("⇄")

with col3:
    target_options = [k for k in LANGUAGES.keys() if k != "🔍 Auto Detect"]
    default_idx = target_options.index("🇺🇸 English")
    target_label = st.selectbox("ภาษาปลายทาง", target_options, index=default_idx)

st.write("")

text_input = st.text_area(
    "✏️ ข้อความที่ต้องการแปล",
    height=160,
    placeholder="พิมพ์หรือวางข้อความที่นี่...",
    max_chars=2000
)

st.caption(f"{len(text_input)} / 2000 ตัวอักษร")

if st.button("✨ แปลภาษา", use_container_width=True, type="primary"):
    if not text_input.strip():
        st.warning("⚠️ กรุณาพิมพ์ข้อความก่อนกดแปล")
    else:
        source_code = LANGUAGES[source_label]
        target_code = LANGUAGES[target_label]

        if source_code != "auto" and source_code == target_code:
            st.warning("⚠️ ภาษาต้นทางและปลายทางต้องไม่เหมือนกัน")
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                st.error("❌ ไม่พบ ANTHROPIC_API_KEY — กรุณาตั้งค่า Environment Variable บน Render")
                st.stop()

            target_name = target_label.split(" ", 1)[-1]

            if source_code == "auto":
                prompt = f"""Detect the language of the following text, then translate it to {target_name}.

Text: {text_input}

Reply ONLY in this JSON format, no markdown, no extra text:
{{"detected_language": "<language name in English>", "translated": "<translated text>"}}"""
            else:
                source_name = source_label.split(" ", 1)[-1]
                prompt = f"""Translate the following text from {source_name} to {target_name}.

Text: {text_input}

Reply ONLY in this JSON format, no markdown, no extra text:
{{"translated": "<translated text>"}}"""

            with st.spinner("🤖 Claude กำลังแปล..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    message = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=1024,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    result = json.loads(message.content[0].text.strip())

                    st.divider()
                    st.subheader("📋 ผลการแปล")

                    if result.get("detected_language"):
                        st.info(f"🔍 ตรวจพบภาษา: **{result['detected_language']}**")

                    st.success(result["translated"])
                    st.code(result["translated"], language=None)
                    st.caption("👆 คลิกที่กล่องโค้ดด้านบนเพื่อ Copy")

                    if "history" not in st.session_state:
                        st.session_state.history = []

                    st.session_state.history.insert(0, {
                        "original": text_input[:60] + ("..." if len(text_input) > 60 else ""),
                        "translated": result["translated"][:60] + ("..." if len(result["translated"]) > 60 else ""),
                        "from": result.get("detected_language") or source_label,
                        "to": target_label,
                    })
                    if len(st.session_state.history) > 5:
                        st.session_state.history.pop()

                except json.JSONDecodeError:
                    st.error("❌ ไม่สามารถอ่านผลลัพธ์จาก AI ได้ ลองใหม่อีกครั้ง")
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")

if "history" in st.session_state and st.session_state.history:
    st.divider()
    st.subheader("📜 ประวัติการแปลล่าสุด")
    for item in st.session_state.history:
        with st.expander(f"🔹 {item['original']}"):
            st.write(f"**จาก:** {item['from']}  →  **{item['to']}**")
            st.write(f"**ผล:** {item['translated']}")

st.divider()
st.caption("Built with ❤️ using Streamlit + Claude AI · LinguaAI v1.0")
