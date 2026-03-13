import streamlit as st
import requests

st.set_page_config(
    page_title="LinguaAI Translator",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 LinguaAI Translator")
st.caption("แปลภาษาฟรี ด้วย Hugging Face AI · ไม่ต้อง API Key")
st.divider()

MODELS = {
    ("en", "th"): "Helsinki-NLP/opus-mt-en-th",
    ("th", "en"): "Helsinki-NLP/opus-mt-th-en",
    ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
    ("fr", "en"): "Helsinki-NLP/opus-mt-fr-en",
    ("en", "de"): "Helsinki-NLP/opus-mt-en-de",
    ("de", "en"): "Helsinki-NLP/opus-mt-de-en",
    ("en", "es"): "Helsinki-NLP/opus-mt-en-es",
    ("es", "en"): "Helsinki-NLP/opus-mt-es-en",
    ("en", "zh"): "Helsinki-NLP/opus-mt-en-zh",
    ("zh", "en"): "Helsinki-NLP/opus-mt-zh-en",
    ("en", "ja"): "Helsinki-NLP/opus-mt-en-jap",
    ("en", "ko"): "Helsinki-NLP/opus-mt-en-ko",
    ("en", "ar"): "Helsinki-NLP/opus-mt-en-ar",
    ("ar", "en"): "Helsinki-NLP/opus-mt-ar-en",
    ("en", "vi"): "Helsinki-NLP/opus-mt-en-vi",
    ("vi", "en"): "Helsinki-NLP/opus-mt-vi-en",
}

LANG_DISPLAY = {
    "th": "🇹🇭 Thai",
    "en": "🇺🇸 English",
    "zh": "🇨🇳 Chinese",
    "ja": "🇯🇵 Japanese",
    "ko": "🇰🇷 Korean",
    "fr": "🇫🇷 French",
    "de": "🇩🇪 German",
    "es": "🇪🇸 Spanish",
    "ar": "🇸🇦 Arabic",
    "vi": "🇻🇳 Vietnamese",
}

DISPLAY_TO_CODE = {v: k for k, v in LANG_DISPLAY.items()}

def get_available_targets(source_code):
    return [LANG_DISPLAY[tgt] for (src, tgt) in MODELS if src == source_code and tgt in LANG_DISPLAY]

def translate_hf(text, model_name):
    API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
    try:
        res = requests.post(API_URL, json={"inputs": text}, timeout=40)
        if res.status_code == 503:
            return None, "⏳ Model กำลัง warm up กรุณารอ 20-30 วินาที แล้วลองใหม่"
        if res.status_code != 200:
            return None, f"❌ Error {res.status_code}"
        data = res.json()
        if isinstance(data, list) and data:
            return data[0].get("translation_text", ""), None
        return None, "❌ ไม่ได้รับผลลัพธ์"
    except requests.exceptions.Timeout:
        return None, "⏱️ หมดเวลา กรุณาลองใหม่"
    except Exception as e:
        return None, f"❌ {str(e)}"

source_options = list(LANG_DISPLAY.values())
col1, col2, col3 = st.columns([5, 1, 5])

with col1:
    source_label = st.selectbox("ภาษาต้นทาง", source_options,
                                 index=source_options.index("🇹🇭 Thai"))

source_code = DISPLAY_TO_CODE[source_label]
available_targets = get_available_targets(source_code)

with col2:
    st.write("")
    st.write("")
    st.write("⇄")

with col3:
    if available_targets:
        def_idx = available_targets.index("🇺🇸 English") if "🇺🇸 English" in available_targets else 0
        target_label = st.selectbox("ภาษาปลายทาง", available_targets, index=def_idx)
    else:
        target_label = st.selectbox("ภาษาปลายทาง", ["🇺🇸 English"])

target_code = DISPLAY_TO_CODE.get(target_label, "en")
model_name = MODELS.get((source_code, target_code))

if not model_name:
    st.warning(f"⚠️ ยังไม่รองรับ {source_label} → {target_label}")

st.write("")
text_input = st.text_area("✏️ ข้อความที่ต้องการแปล", height=160,
                           placeholder="พิมพ์หรือวางข้อความที่นี่...", max_chars=500)
st.caption(f"{len(text_input)} / 500 ตัวอักษร")

if st.button("✨ แปลภาษา", use_container_width=True, type="primary", disabled=not model_name):
    if not text_input.strip():
        st.warning("⚠️ กรุณาพิมพ์ข้อความก่อนกดแปล")
    else:
        with st.spinner(f"🤖 กำลังแปล {source_label} → {target_label} ..."):
            translated, error = translate_hf(text_input, model_name)

        if error:
            st.error(error)
        else:
            st.divider()
            st.subheader("📋 ผลการแปล")
            st.success(translated)
            st.code(translated, language=None)
            st.caption("👆 คลิกที่กล่องโค้ดด้านบนเพื่อ Copy")

            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.insert(0, {
                "original": text_input[:60] + ("..." if len(text_input) > 60 else ""),
                "translated": translated[:60] + ("..." if len(translated) > 60 else ""),
                "from": source_label, "to": target_label,
            })
            if len(st.session_state.history) > 5:
                st.session_state.history.pop()

if "history" in st.session_state and st.session_state.history:
    st.divider()
    st.subheader("📜 ประวัติการแปลล่าสุด")
    for item in st.session_state.history:
        with st.expander(f"🔹 {item['original']}"):
            st.write(f"**จาก:** {item['from']}  →  **{item['to']}**")
            st.write(f"**ผล:** {item['translated']}")

st.divider()
st.caption("Built with ❤️ using Streamlit + Hugging Face · LinguaAI v2.0 · ฟรี 100%")
