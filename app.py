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
                
                # 核心分析指令：導入全領域動態辨識與無痕評估邏輯
                prompt = f"""
                你是一套專為「幼教老師」設計的專業發展評估 AI 系統。
                請結合圖片與以下資訊撰寫【提供給老師內部參考】的專業報告：
                - 幼兒姓名：{child_name}
                - 幼兒年齡：{child_age}
                - 老師補充：{teacher_notes if teacher_notes else "無"}

                ⚠️ 【最高指導原則：現場觀察者視角】
                1. 絕對禁止出現「照片中」、「畫面中」、「未見」、「推測」等看圖說故事的字眼。
                2. 絕對禁止描述幼兒穿著、口罩或與活動能力無關的環境背景。
                3. 完全代入「現場老師」第一人稱視角，用肯定句描述正在發生的客觀事實。

                請依照以下結構輸出：

                ### 👁️ 【{child_name} 的活動紀錄】
                直接切入幼兒的操作歷程。將「老師補充」的內容無縫轉化為觀察事實，不要描述背景環境。

                ### 📈 【發展領域分析】
                對應教育部幼教六大領域，直接說明孩子當下的行為展現了什麼能力。嚴禁寫出「雖然未見對話...」等揣測語，請依事實論述。

                ### 🌟 【現有能力評估】
                請將評估邏輯「無痕」融入流暢、溫和的段落中，絕對不要列出 1. 2. 3. 標號或子標題。
                ⚠️ 嚴禁使用「依據常模」、「對照其實際年齡」等生硬語句，請代入專業老師口吻執行以下邏輯：
                - **識別領域與指標**：自動辨識活動屬於哪個領域（如：精細動作、美感創作、大肌肉協調、視覺空間等），並定位該任務的發展門檻。
                - **實齡動態比對**：
                    1. 若任務難度低於實齡：描述為「基礎經驗的深耕」，肯定其穩定度，說明正為高階技能紮根。
                    2. 若任務具高度挑戰性：肯定其「面對挑戰的韌性」或「跨階展現的潛能」，避免比較性字眼。
                    3. 若符合實齡：描述為「發展步調的穩健與自信」。
                - **未來發展意義**：總結此行為對孩子下一個發展階段的重要性。

                ### 🌱 【智慧鷹架引導】
                * **引發思考的提問**：提供 2 個開放式問題。
                * **具體延伸玩法**：提供 1 個難度 +1 的遊戲建議。

                ### 📝 【親師溝通筆記】
                唯一提供給「家長」看的內容（約150字）。採用「三步溝通法」：
                - 第一步：肯定亮點（描述孩子「已經做到」的微小事實）。
                - 第二步：事實與專業解讀（以「發展中」取代「落後」）。
                - 第三步：親師攜手建議（提供家中可進行的具體練習）。

                請保持日系風格的溫暖感，適度使用🌸、🍃等符號裝飾。
                """
                
                response = model.generate_content([prompt, img])
                
                # 渲染結果
                st.subheader("📋 專業觀察分析報告")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"系統忙碌中，請檢查設定或稍後再試。")
    else:
        st.warning("請填寫姓名、年齡並上傳照片喔！")

# 頁尾
st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與探索中萌芽 🍃</p>", unsafe_allow_html=True)
