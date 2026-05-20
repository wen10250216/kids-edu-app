import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 網頁風格設定 (日系手繪療育風)
st.set_page_config(page_title="幼兒學習發展分析系統", page_icon="🌿", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    h1 { color: #4e342e !important; text-align: center; font-weight: bold; }
    div.stButton > button:first-child {
        background-color: #ffccbc !important;
        color: #5d4037 !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100% !important;
        padding: 10px !important;
    }
    .report-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #eee;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 模型設定
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ 尚未設定 API Key")

try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
    model = genai.GenerativeModel(target_model)
except:
    model = genai.GenerativeModel('gemini-1.5-flash')

# 3. 介面呈現
st.markdown("<h1>🌿 幼兒觀察與親師共育系統</h1>", unsafe_allow_html=True)
st.divider()

col_name, col_age = st.columns(2)
with col_name:
    child_name = st.text_input("🎨 幼兒姓名", placeholder="小芽")
with col_age:
    child_age = st.text_input("🎈 幼兒年齡", placeholder="例如：5歲2個月")

teacher_notes = st.text_area("✍️ 老師的補充觀察 (選填)", placeholder="例如：今天挑戰積木時，雖然倒了三次但還是笑著說要蓋更堅固的...")

uploaded_file = st.file_uploader("🖼️ 上傳作品或行為照片", type=["jpg", "jpeg", "png"])

# 4. 執行分析
if st.button("✨ 生成專業觀察紀錄"):
    if uploaded_file and child_age and child_name:
        with st.spinner(f"正在為 {child_name} 撰寫專業觀察紀錄..."):
            try:
                img = Image.open(uploaded_file)
                
                # 嚴格校準後的專業指令
                prompt = f"""
                你是一位資深的幼兒教育專家。請觀察照片並根據以下資訊撰寫報告：
                - 幼兒：{child_name} ({child_age})
                - 老師補充：{teacher_notes if teacher_notes else "無"}

                請嚴格依照以下格式輸出：

                ### 👁️ 【{child_name} 的活動紀錄】
                (具體描述作品形狀、空間結構與美感，並融入老師的補充細節)

                ### 📈 【發展領域分析】
                (精確對應幼教六大領域之發展意義)

                ### 🌟 【現有能力評估】
                (對比 {child_age} 常模，給予正向肯定的專業評量)

                ### 🌱 【智慧鷹架引導】
                * **具體提問**：(設計 2 個引發思考的開放式問題)
                * **延伸玩法**：(提供 1 個可執行的後續活動建議)

                ### 📝 【親師溝通建議】
                字數請嚴格控制在 150 字左右。請採用以下三段式結構書寫，對象為家長：
                1. **點出具體事件**：描繪今天在學校觀察到的特定行為或情境。
                2. **分析與肯定成長**：說明此行為背後的教育價值與孩子的進步亮點。
                3. **建議(給家長的話)**：提供一個家中可配合或嘗試的具體育兒方向。

                語氣：溫暖、專業、正向，並使用 🌸, 🍃 等療育符號。
                """
                
                response = model.generate_content([prompt, img])
                st.markdown("<div class='report-card'>", unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"系統忙碌中，請稍後再試。")
    else:
        st.warning("請填寫姓名、年齡並上傳照片。")
