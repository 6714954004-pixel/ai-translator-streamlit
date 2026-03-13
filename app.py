import streamlit as st
import requests

st.set_page_config(
    page_title="LinguaAI Translator",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 LinguaAI Translator")
st.caption("แปลภาษาฟรี 100% · ไม่ต้อง API Key · Powered by MyMemory")
st.divider()

LANGUAGES = {
    "🇹🇭 Thai":       "th",
    "🇺🇸 English":    "en",
    "🇨🇳 Chinese":    "zh",
    "🇯🇵 Japanese":   "ja",
    "🇰🇷 Korean":     "ko",
    "🇫🇷 French":     "fr",
    "🇩🇪 German":     "de",
    "🇪🇸 Spanish":    "es",
    "🇸🇦 Arabic":     "ar",
    "🇻🇳 Vietnamese": "vi",
    "🇷🇺 Russian":    "ru",
    "🇮🇳 Hindi":      "hi",
}
DISPLAY_TO_CODE = {label: code for label, code in LANGUAGES.items()}

def translate(text, src_code, tgt_code):
    url = "https://api.mymemory.translated.net/get"
    params = {
        "q": text,
        "langpair": f"{src_code}|{tgt_code}"
    }
    try:
        res = requests.get(url, params=params, timeout=15)
        if res.status_code != 200:
            return None, f"❌ HTTP Error {res.status_code}"
        data = res.json()
        status = data.get("responseStatus", 0)
        if status == 200:
            translated = data["responseData"]["translatedText"]
            # เช็คว่าผลลัพธ์ไม่ใช่ error message
            if "MYMEMORY WARNING" in translated:
                return None, "⚠️ เกินโควต้าวันนี้ (5,000 ตัวอักษร/วัน) กรุณาลองใหม่พรุ่งนี้"
            return translated, None
        elif status == 429:
            return None, "⚠️ เกินโควต้าวันนี้ กรุณาลองใหม่พรุ่งนี้"
        else:
            return None, f"❌ Error: {data.get('responseDetails', 'Unknown error')}"
    except requests.exceptions.Timeout:
        return None, "⏱️ หมดเวลา กรุณาลองใหม่"
    except Exception as e:
        return None, f"❌ {str(e)}"

# --- UI ---
lang_options = list(LANGUAGES.keys())

col1, col2, col3 = st.columns([5, 1, 5])
with col1:
    src_label = st.selectbox("ภาษาต้นทาง", lang_options,
                              index=lang_options.index("🇹🇭 Thai"))
with col2:
    st.markdown("<div style='text-align:center;padding-top:28px;font-size:1.3rem'>⇄</div>",
                unsafe_allow_html=True)
with col3:
    tgt_options = [l for l in lang_options if l != src_label]
    default_tgt = tgt_options.index("🇺🇸 English") if "🇺🇸 English" in tgt_options else 0
    tgt_label = st.selectbox("ภาษาปลายทาง", tgt_options, index=default_tgt)

src_code = DISPLAY_TO_CODE[src_label]
tgt_code = DISPLAY_TO_CODE[tgt_label]

st.write("")
text_input = st.text_area(
    "✏️ ข้อความที่ต้องการแปล",
    height=160,
    placeholder="พิมพ์หรือวางข้อความที่นี่...",
    max_chars=500
)
st.caption(f"{len(text_input)} / 500 ตัวอักษร")

if st.button("✨ แปลภาษา", use_container_width=True, type="primary"):
    if not text_input.strip():
        st.warning("⚠️ กรุณาพิมพ์ข้อความก่อนกดแปล")
    elif src_code == tgt_code:
        st.warning("⚠️ ภาษาต้นทางและปลายทางต้องไม่เหมือนกัน")
    else:
        with st.spinner(f"🌐 กำลังแปล {src_label} → {tgt_label} ..."):
            result, error = translate(text_input, src_code, tgt_code)

        if error:
            st.error(error)
        else:
            st.divider()
            st.subheader("📋 ผลการแปล")
            st.success(result)
            st.code(result, language=None)
            st.caption("👆 คลิกที่กล่องโค้ดด้านบนเพื่อ Copy")

            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.insert(0, {
                "original": text_input[:60] + ("..." if len(text_input) > 60 else ""),
                "translated": result[:60] + ("..." if len(result) > 60 else ""),
                "from": src_label,
                "to": tgt_label,
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
st.caption("Built with ❤️ using Streamlit + MyMemory API · LinguaAI v3.0 · ฟรี 100%")