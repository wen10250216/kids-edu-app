import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 網頁風格設定 (日系馬卡龍療育風)
st.set_page_config(page_title="幼兒學習發展分析系統", page_icon="🍃", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #f0f7fa; /* 淡藍色水彩感底色 */
    }
    .stButton>button {
        background-color: #ffccbc; /* 馬卡龍淡橘色按鈕 */
        color: #5d4037;
        border-radius: 20px;
        border: none;
        padding: 10px 25px;
        font-weight: bold;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    h1 {
        color: #4a6572;
        text-align: center;
        font-weight: bold;
    }
    .stSubheader {
        color: #546e7a;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 安全讀取 API Key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ 尚未在 Streamlit Secrets 中偵測到 API Key")

# --- 終極模型修正：自動偵測可用型號 (確保不跳 404) ---
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model_name = next((m for m in available_models if 'gemini-1.5-flash' in m), 
                            next((m for m in available_models if 'gemini-pro-vision' in m), available_models[0]))
    model = genai.GenerativeModel(target_model_name)
except Exception as e:
    model = genai.GenerativeModel('gemini-1.5-flash') # 保底方案
# -----------------------------------

# 3. 介面呈現
st.title("🌿 幼兒學習發展分析系統")
st.markdown("<p style='text-align: center; color: #78909c;'>結合 AI 視覺辨識，給予最溫暖的適性教學建議</p>", unsafe_allow_html=True)
st.divider()

st.subheader("📸 幼兒互動紀錄")
col_upload, col_age = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader("上傳幼兒作品或遊戲照片", type=["jpg", "jpeg", "png"])

with col_age:
    child_age = st.text_input("🎈 兒童年齡", placeholder="例如：5歲9個月")

st.divider()

# 4. 執行分析
if st.button("✨ 開始智能分析", use_container_width=True):
    if uploaded_file and child_age:
        with st.spinner("AI 老師正在用心觀察孩子的成長..."):
            try:
                img = Image.open(uploaded_file)
                prompt = f"""
                你是一位資深的幼兒教育專家。請觀察照片中幼兒的作品或行為，
                並根據年齡「{child_age}」進行專業分析。
                請依照以下標題與 Markdown 格式排版：
                ### 👁️ 【幼兒觀察紀錄】
                ### 📈 【發展領域分析】
                ### 🌟 【現有能力評估】
                ### 🌱 【智慧鷹架引導】
                ### 📝 【老師筆記】
                語氣請保持日系療育感，內容要豐富具體。
                """
                response = model.generate_content([prompt, img])
                
                # 結果區域
                st.subheader("📋 智能分析報告")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"分析失敗：{e}")
    else:
        st.warning("請記得上傳照片並輸入年齡喔！")

st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與智慧中發芽 🍃</p>", unsafe_allow_html=True)
