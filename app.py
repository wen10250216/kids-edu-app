import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 網頁風格設定
st.set_page_config(page_title="幼兒學習發展分析系統", page_icon="🌿", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7fa !important; }
    h1 { color: #5d707a !important; text-align: center; font-weight: bold; }
    div.stButton > button:first-child {
        background-color: #ffccbc !important;
        color: #5d4037 !important;
        border-radius: 25px !important;
        border: 2px solid #ffb6a0 !important;
        font-weight: bold !important;
        width: 100% !important;
        padding: 10px !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05) !important;
    }
    .report-card {
        background: rgba(255, 255, 255, 0.85);
        padding: 30px;
        border-radius: 20px;
        border-left: 10px solid #b2dfdb;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05);
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 安全讀取 API Key
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
st.markdown("<h1>🌿 幼兒學習發展分析系統</h1>", unsafe_allow_html=True)
st.divider()

col_name, col_age = st.columns(2)
with col_name:
    child_name = st.text_input("🎨 幼兒姓名 / 暱稱", placeholder="例如：雅雅")
with col_age:
    child_age = st.text_input("🎈 幼兒年齡", placeholder="例如：5歲9個月")

teacher_notes = st.text_area("✍️ 老師的補充觀察 (選填)", 
                            placeholder="描述孩子的口語、動作、遇到挑戰時的反應等，能讓 AI 評估更準確。")

uploaded_file = st.file_uploader("🖼️ 上傳觀察照片", type=["jpg", "jpeg", "png"])

# 4. 執行分析
if st.button("✨ 生成專業觀察報告"):
    if uploaded_file and child_age and child_name:
        with st.spinner(f"正在為 {child_name} 產出教師專屬評估報告..."):
            try:
                img = Image.open(uploaded_file)
                
                # 核心分析指令
                prompt = f"""
                你是一套專為「幼教老師」設計的專業發展評估 AI 系統。
                請觀察照片並結合以下資訊撰寫【提供給老師內部參考】的專業報告：
                - 幼兒姓名：{child_name}
                - 幼兒年齡：{child_age}
                - 老師補充：{teacher_notes if teacher_notes else "無"}

                請嚴格遵守以下規則：
                1. 報告前四個區塊的受眾是「老師」，請勿出現「親愛的家長您好」等問候語，請直接切入專業分析。
                2. 必須將「老師補充」的內容【無縫消化並融合】到活動紀錄中。絕對不能寫出「老師筆記提到」、「根據老師補充」等字眼，請直接將其轉化為客觀發生的情境事實。

                請依照以下結構輸出，語氣需專業、客觀且具教育啟發性：

                ### 👁️ 【{child_name} 的活動紀錄】
                客觀描述照片中的活動類型與操作事實。請將補充資訊自然地融入情境描述中，描繪出一個連貫的活動畫面。

                ### 📈 【發展領域分析】
                對應教育部幼教六大領域，說明此行為對該年齡層的能力價值。

                ### 🌟 【現有能力評估】
                請執行「發展對照」判斷：
                1. 判斷任務難度：分析照片活動（如 1:1 配對、3D 建構、單腳跳等）對應的常見年齡。
                2. 實齡對比：對照「{child_age}」，定性孩子目前處於「發展萌芽期」、「鞏固期」或「熟練期」。
                3. 誠實觀測：若能力低於實齡，請描述為「正致力於基礎經驗的積累」，嚴禁給予無根據的誇獎。

                ### 🌱 【智慧鷹架引導】
                * **引發思考的提問**：提供 2 個開放式問題，供老師在現場引導幼兒。
                * **具體延伸玩法**：提供 1 個難度 +1 的遊戲建議，供老師佈置學習區參考。

                ### 📝 【親師溝通筆記】
                此區塊是唯一要提供給「家長」看的內容。字數嚴格控制在 150 字上下。請採用「三步溝通法」架構書寫：
                - **第一步：肯定亮點**：描述孩子在該情境中「已經做到」的微小事實或正向態度（緩解防衛心）。
                - **第二步：事實與專業解讀**：以「發展中」取代「落後」，解釋行為背後的領域意義與孩子目前的發展路徑。
                - **第三步：親師攜手建議**：提供一個家中可隨手進行、遊戲化的具體練習建議。

                請保持日系風格的溫暖感，適度使用🌸、🍃等符號裝飾。
                """
                
                response = model.generate_content([prompt, img])
                st.markdown("<div class='report-card'>", unsafe_allow_html=True)
                st.subheader("📋 專業觀察分析報告")
                st.markdown(response.text)
                st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"系統忙碌中，請檢查 API 設定或稍後再試。")
    else:
        st.warning("請填寫姓名、年齡並上傳照片喔！")

st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與智慧中發芽 🍃</p>", unsafe_allow_html=True)
