import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 網頁風格設定 (日系馬卡龍色系)
st.set_page_config(page_title="幼兒學習發展分析系統", page_icon="🍃", layout="centered")

# 使用自定義 CSS 來美化介面
st.markdown("""
    <style>
    .main {
        background-color: #f0f7fa; /* 淡藍色底 */
    }
    .stButton>button {
        background-color: #ffccbc; /* 馬卡龍淡橘色按鈕 */
        color: #5d4037;
        border-radius: 20px;
        border: none;
        padding: 10px 25px;
        font-weight: bold;
    }
    h1 {
        color: #4a6572;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 🔑 【金鑰讀取區】
# 這裡不需要「手動貼上」金鑰，它會自動抓取你在 Streamlit Secrets 設定的值
# ---------------------------------------------------------
if "GEMINI_API_KEY" in st.secrets:
    # 這裡的 st.secrets["GEMINI_API_KEY"] 就是對應你在黑色框框填寫的內容
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ 尚未在 Streamlit Secrets 中偵測到 API Key，請檢查設定！")
# ---------------------------------------------------------

# 建立模型
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. 網頁標題與副標
st.title("🌿 幼兒學習發展分析系統")
st.markdown("<p style='text-align: center;'>結合 AI 視覺辨識，給予最溫暖的適性教學建議</p>", unsafe_allow_html=True)
st.divider()

# 4. 幼兒互動紀錄區
st.subheader("📸 幼兒互動紀錄")
col_upload, col_age = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader("上傳幼兒作品或遊戲照片", type=["jpg", "jpeg", "png"])

with col_age:
    child_age = st.text_input("🎈 兒童年齡", placeholder="例如：5歲9個月")

st.divider()

# 5. 執行分析
if st.button("✨ 開始智能分析", use_container_width=True):
    if uploaded_file and child_age:
        with st.spinner("AI 老師正在用心觀察孩子的成長..."):
            try:
                img = Image.open(uploaded_file)
                
                # 分析指令
                prompt = f"""
                你是一位資深的幼兒教育專家。請觀察照片中幼兒的作品或行為，
                並根據年齡「{child_age}」進行專業分析。
                請嚴格依照以下標題進行 Markdown 排版：
                ### 👁️ 【幼兒觀察紀錄】
                ### 📈 【發展領域分析】
                ### 🌟 【現有能力評估】
                ### 🌱 【智慧鷹架引導】
                ### 📝 【老師筆記】
                語氣請保持日系療育、溫柔感。
                """
                
                response = model.generate_content([prompt, img])
                
                st.subheader("📝 智能分析報告")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"分析過程出現錯誤：{e}")
    else:
        st.warning("請記得先上傳照片並填寫孩子的年齡喔！")

st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與智慧中發芽 🍃</p>", unsafe_allow_html=True)
