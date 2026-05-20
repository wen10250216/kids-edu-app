import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 網頁風格設定 (日系手繪療育風)
st.set_page_config(page_title="幼兒學習發展分析系統", page_icon="🍃", layout="centered")

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
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05) !important;
    }
    .report-card {
        background: rgba(255, 255, 255, 0.8);
        padding: 25px;
        border-radius: 20px;
        border-left: 10px solid #b2dfdb;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 安全讀取 API Key 與模型初始化
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ 尚未偵測到 API Key")

try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model_name = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
    model = genai.GenerativeModel(target_model_name)
except:
    model = genai.GenerativeModel('gemini-1.5-flash')

# 3. 介面呈現
st.markdown("<h1>🌿 幼兒學習發展分析系統</h1>", unsafe_allow_html=True)
st.divider()

st.subheader("📸 幼兒互動紀錄")
col_name, col_age = st.columns(2)
with col_name:
    child_name = st.text_input("🎨 幼兒姓名或暱稱", placeholder="例如：小芽")
with col_age:
    child_age = st.text_input("🎈 幼兒年齡", placeholder="例如：5歲2個月")

uploaded_file = st.file_uploader("🖼️ 上傳作品或行為照片", type=["jpg", "jpeg", "png"])
st.divider()

# 4. 執行分析
if st.button("✨ 開始智能分析"):
    if uploaded_file and child_age and child_name:
        with st.spinner(f"AI 老師正在用心觀察 {child_name} 的成長回憶..."):
            try:
                img = Image.open(uploaded_file)
                
                # 精確調整後的專業指令
                prompt = f"""
                你是一位資深的幼兒教育專家。請觀察照片並根據以下資訊進行分析：
                - 幼兒姓名：{child_name}
                - 幼兒年齡：{child_age}

                請全程使用溫暖、療育且正向的語氣，嚴格依照以下格式排版：

                ### 👁️ 【{child_name} 的觀察紀錄】
                請詳細描述作品的形狀（如幾何特徵）、結構（如空間堆疊、對稱性）與色彩運用的美感特徵。

                ### 📈 【發展領域分析】
                請針對幼兒教育六大領域（身體動作、認知、語文、社會、情緒、美感），分析 {child_name} 在這張照片中具體展現了哪些領域的發展。

                ### 🌟 【現有能力評估】
                第一句話請務必對比「{child_age}」的發展常模，具體描述 {child_name} 是穩定達標、展現超越年齡的潛力，或是處於發展中的階段（請避免負面詞彙，如「遲緩」請改用「尚有發展空間」或「萌芽期」）。接著描述其展現出的優勢能力。

                ### 🌱 【智慧鷹架引導】
                * **具體提問一**：(針對作品細節的開放式問題)
                * **具體提問二**：(引發思考或動機的問題)
                * **延伸玩法**：(建議一個具體的後續延伸活動，幫助其能力更上一層樓)

                ### 📝 【給老師的小筆記】
                請撰寫一段約 100 字、專業且充滿溫度的文字，適合老師直接應用於聯絡簿、作品集或個別化觀察紀錄中。

                語氣請多使用溫暖的形容詞，並適度加入日系風格的符號（如 🌸, 🍃, ✨）。
                """
                
                response = model.generate_content([prompt, img])
                
                # 呈現結果
                st.markdown("<div class='report-card'>", unsafe_allow_html=True)
                st.subheader("📋 智能分析報告")
                st.markdown(response.text)
                st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"分析失敗，錯誤訊息：{e}")
    else:
        st.warning("請完整提供姓名、年齡並上傳照片喔！")

st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與智慧中發芽 🍃</p>", unsafe_allow_html=True)
