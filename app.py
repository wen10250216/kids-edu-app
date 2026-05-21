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
    .stMarkdown {
        line-height: 1.8;
        color: #37474f;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 安全讀取 API Key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ 尚未設定 API Key，請檢查 Streamlit Secrets 設定。")

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
        with st.spinner(f"正在為 {child_name} 產生專屬評估報告..."):
            try:
                img = Image.open(uploaded_file)
                
                # 核心分析指令：修正報告首句稱謂
                prompt = f"""
                你是一套專為「幼教老師」設計的專業發展評估 AI 系統。
                請觀察照片並結合以下資訊，產出一份【關於 {child_name} 的專業發展評估報告】，供老師內部參考：
                - 幼兒姓名：{child_name}
                - 幼兒年齡：{child_age}
                - 老師補充：{teacher_notes if teacher_notes else "無"}

                ⚠️ 【最高指導原則：現場觀察者視角】
                1. 絕對禁止出現「照片中」、「畫面中」、「未見」、「推測」等看圖說故事的字眼。
                2. 絕對禁止描述與能力無關的穿著、配件或背景。
                3. 請完全代入「現場老師」視角，直接用肯定句描述正在發生的客觀事實。
                4. 報告開頭第一句話請直接標明：這是一份關於 {child_name} 的專業發展評估報告，供老師內部參考。

                請依照以下結構輸出：

                ### 👁️ 【{child_name} 的活動紀錄】
                直接切入幼兒的操作歷程。將補充內容無痕轉化為觀察事實。

                ### 📈 【發展領域分析】
                對應教育部幼教六大領域，直接說明孩子當下的行為展現。

                ### 🌟 【現有能力評估】
                請將評估邏輯「無痕」融入流暢、溫和的段落中。
                ⚠️ 嚴禁使用「依據常模」等檢核表句型，請代入老師口吻：
                - 識別領域與難度定位。
                - 實齡動態比對（若難度低於年齡，描述為基礎深耕；若具挑戰性，肯定韌性與潛能）。
                - 描述行為對下一個發展階段的重要性。

                ### 🌱 【智慧鷹架引導】
                * 引發思考的提問：2 個開放式問題。
                * 具體延伸玩法：1 個難度 +1 的建議。

                ### 📝 【親師溝通筆記】
                給家長看的內容（約150字），採用「三步溝通法」：
                - 第一步：肯定亮點。
                - 第二步：事實與專業解讀（發展中）。
                - 第三步：親師攜手建議。

                保持日系溫暖感，適度使用🌸、🍃等符號。
                """
                
                response = model.generate_content([prompt, img])
                
                # 渲染結果
                st.subheader("📋 專業觀察分析報告")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"系統忙碌中，請稍後再試。")
    else:
        st.warning("請填寫姓名、年齡並上傳照片喔！")

st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與探索中萌芽 🍃</p>", unsafe_allow_html=True)
