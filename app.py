import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 網頁風格設定 (日系手繪療育風強化版)
st.set_page_config(page_title="幼兒學習發展分析系統", page_icon="🌿", layout="centered")

st.markdown("""
    <style>
    /* 全域背景：淡藍色水彩感 */
    .stApp {
        background-color: #f0f7fa !important;
    }
    
    /* 標題與字體設定 */
    h1 {
        color: #5d707a !important;
        font-family: 'Noto Sans TC', sans-serif !important;
        text-align: center;
        font-weight: bold;
    }
    
    /* 按鈕樣式：馬卡龍橘色 */
    div.stButton > button:first-child {
        background-color: #ffccbc !important;
        color: #5d4037 !important;
        border-radius: 25px !important;
        border: 2px solid #ffb6a0 !important;
        padding: 0.6rem 2rem !important;
        font-size: 18px !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05) !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #ffbba7 !important;
        transform: translateY(-2px);
    }

    /* 報告區塊裝飾 (卡片感) */
    .report-card {
        background: rgba(255, 255, 255, 0.85);
        padding: 30px;
        border-radius: 20px;
        border-left: 10px solid #b2dfdb;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05);
        margin-top: 20px;
        color: #37474f;
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 安全讀取 API Key 與模型初始化
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ 尚未在 Streamlit Secrets 中設定 API Key")

try:
    # 自動偵測可用型號，確保不跳 404 錯誤
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
    model = genai.GenerativeModel(target_model)
except:
    model = genai.GenerativeModel('gemini-1.5-flash')

# 3. 介面呈現
st.markdown("<h1>🌿 幼兒學習發展分析系統</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #78909c;'>結合 AI 視覺辨識與專業發展指標，給予親師最溫暖的適性教學建議</p>", unsafe_allow_html=True)
st.divider()

# 幼兒觀察紀錄區
st.subheader("📸 幼兒觀察紀錄")
col_name, col_age = st.columns(2)
with col_name:
    child_name = st.text_input("🎨 幼兒姓名 / 暱稱", placeholder="例如：默默")
with col_age:
    child_age = st.text_input("🎈 幼兒年齡", placeholder="例如：6歲3個月")

teacher_notes = st.text_area("✍️ 老師的補充觀察 (選填)", 
                            placeholder="描述孩子操作時的對話、情緒反應或挑戰過程，能讓分析更精準喔！")

uploaded_file = st.file_uploader("🖼️ 上傳觀察照片 (教具操作、美感創作、大肢體活動等)", type=["jpg", "jpeg", "png"])

st.divider()

# 4. 執行分析
if st.button("✨ 開始智能分析報告"):
    if uploaded_file and child_age and child_name:
        with st.spinner(f"正在對照發展常模，為 {child_name} 撰寫專業觀察紀錄..."):
            try:
                img = Image.open(uploaded_file)
                
                # 核心分析指令 (Prompt)
                prompt = f"""
                你是一位資深的幼兒教育專家與發展評估顧問。請觀察照片內容（包括但不限於精細動作、認知教具、大肌肉、藝術創作等），並結合以下資訊進行深度分析：
                - 幼兒姓名：{child_name}
                - 幼兒年齡：{child_age}
                - 老師筆記：{teacher_notes if teacher_notes else "無"}

                請全程使用溫暖、專業、療育且正向的語氣，嚴格依照以下格式輸出：

                ### 👁️ 【{child_name} 的活動紀錄】
                描述孩子正在進行的活動。請精確辨識活動類型與操作特徵（例如：1:1 平面配對、3D 空間建構、粗大動作平衡、動態藝術創作等）。

                ### 📈 【發展領域分析】
                對應教育部幼兒園課程綱要六大領域，分析此活動對 {child_name} 展現的核心能力價值。

                ### 🌟 【現有能力評估：發展指標對照】
                請嚴格執行以下評估邏輯：
                1. 任務難度分析：判斷照片中活動任務對應的發展年齡。
                2. 實齡對比：將任務難度與「{child_age}」進行客觀比對。
                3. 專業定性：
                   - 若任務難度明顯低於實齡：請稱讚其操作的「穩定度」與「專注力」，但必須專業指出目前處於「基礎紮根階段」，並建議朝向更具挑戰性的目標（如脫離範本）邁進。
                   - 若任務難度符合或超越實齡：給予具體的教育意義解讀。
                *嚴禁使用「落後」等負面詞彙，請改用「鞏固期」或「萌芽期」。*

                ### 🌱 【智慧鷹架引導】
                * **引發思考的提問**：提供 2 個具體的提問方式，引導其思考或進階操作。
                * **階梯延伸玩法**：提供 1 個難度加一（+1）的具體延伸建議。

                ### 📝 【親師溝通筆記】
                字數請嚴格控制在 150 字上下。請採用以下結構書寫，受眾為家長：
                1. **點出具體事件**：描繪今天觀察到的具體情境事實。
                2. **分析與肯定成長**：解釋行為背後的專業價值，並肯定其亮點或進步。
                3. **建議(給家長的話)**：提供家長回家後可攜手合作的具體育兒方向。

                請全程使用日系風格符號裝飾（如 🌸, 🍃, ✨, 🍬）。
                """
                
                response = model.generate_content([prompt, img])
                
                # 呈現結果
                st.markdown("<div class='report-card'>", unsafe_allow_html=True)
                st.subheader("📋 專業發展觀察報告")
                st.markdown(response.text)
                st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"系統暫時無法處理，請檢查照片格式或 API 狀態。")
    else:
        st.warning("請完整填寫幼兒姓名、年齡，並上傳照片喔！")

st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與智慧中發芽 🍃</p>", unsafe_allow_html=True)
