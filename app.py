import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 網頁風格設定 (強效 CSS 版)
st.set_page_config(page_title="幼兒學習發展分析系統", page_icon="🍃", layout="centered")

# 將 CSS 樣式直接注入
st.markdown("""
    <style>
    /* 全域背景色 - 淡藍色水彩感 */
    .stApp {
        background-color: #f0f7fa !important;
    }
    
    /* 按鈕樣式 - 馬卡龍橘色 */
    div.stButton > button:first-child {
        background-color: #ffccbc !important;
        color: #5d4037 !important;
        border-radius: 20px !important;
        border: 2px solid #ffab91 !important;
        padding: 0.5rem 2rem !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05) !important;
    }

    /* 標題樣式 */
    h1 {
        color: #4a6572 !important;
        font-family: 'Noto Sans TC', sans-serif !important;
    }
    
    /* 分隔線顏色 */
    hr {
        border-top: 1px solid #cfd8dc !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 安全讀取 API Key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ 尚未在 Streamlit Secrets 中偵測到 API Key")

# --- 自動偵測可用型號 ---
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model_name = next((m for m in available_models if 'gemini-1.5-flash' in m), 
                            next((m for m in available_models if 'gemini-pro-vision' in m), available_models[0]))
    model = genai.GenerativeModel(target_model_name)
except:
    model = genai.GenerativeModel('gemini-1.5-flash')

# 3. 介面呈現
st.markdown("<h1 style='text-align: center;'>🌿 幼兒學習發展分析系統</h1>", unsafe_allow_html=True)
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
if st.button("✨ 開始智能分析"):
    if uploaded_file and child_age:
        with st.spinner("AI 老師正在用心觀察孩子的成長..."):
            try:
                img = Image.open(uploaded_file)
                prompt = f"""
                你是一位資深的幼兒教育專家。請觀察照片中幼兒的作品或行為，
                並根據年齡「{child_age}」進行專業分析。
                請依照以下標題排版：
                ### 👁️ 【幼兒觀察紀錄】
                ### 📈 【發展領域分析】
                ### 🌟 【現有能力評估】
                ### 🌱 【智慧鷹架引導】
                ### 📝 【老師筆記】
                語氣請保持日系療育感，並使用表情符號點綴。
                """
                response = model.generate_content([prompt, img])
                st.subheader("📋 智能分析報告")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"分析失敗：{e}")
    else:
        st.warning("請記得上傳照片並輸入年齡喔！")

st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與智慧中發芽 🍃</p>", unsafe_allow_html=True)
