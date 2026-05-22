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
    child_name = st.text_input("🎨 幼兒姓名 / 暱稱", placeholder="例如：嘉嘉")
with col_age:
    child_age = st.text_input("🎈 幼兒年齡", placeholder="例如：5歲")

teacher_notes = st.text_area("✍️ 老師的補充觀察 (選填)", 
                            placeholder="描述孩子的口語、動作、遇到挑戰時的反應或當時的情境等，能讓評估報告更準確。")

uploaded_file = st.file_uploader("🖼️ 上傳觀察照片", type=["jpg", "jpeg", "png"])

# 4. 執行分析
if st.button("✨ 生成專業觀察報告"):
    if uploaded_file and child_age and child_name:
        with st.spinner(f"正在為 {child_name} 產生專屬評估報告..."):
            try:
                img = Image.open(uploaded_file)
                
                # 核心分析指令：將「術語標籤」徹底轉換為「狀態描述」
                prompt = f"""
                你是一套專業的幼教發展評估 AI 系統。請根據照片與以下資訊產出報告：
                - 幼兒姓名：{child_name}
                - 幼兒年齡：{child_age}
                - 老師補充：{teacher_notes if teacher_notes else "無"}

                ⚠️ 【最高指導原則：嚴禁臆測事實與看圖說故事】
                1. 嚴禁使用「專注、細心、耐心」等心理揣測詞，除非筆記有提。
                2. 嚴禁描述衣著顏色、背景雜物。請直接描述【能力展現事實】。
                3. 報告第一句：這是一份關於 {child_name} 的專業發展評估報告，供老師參考。

                請依照以下結構輸出：

                ### 👁️ 【{child_name} 的活動紀錄】
                直接描述活動中的能力展現事實，並將老師補充資訊自然內化為觀察細節。

                ### 📈 【發展領域分析】
                對應教育部幼教六大領域，精確論述展現的具體能力指標。

                ### 🌟 【現有能力評估】
                請將評估邏輯分為「兩段」清晰的文字敘述，嚴禁標註數字、小標題或生硬術語（如依據常模）：

                第一段（能力判斷）：
                請直接將辨識出的活動，精準對應「六大領域」與「發展常模」，開頭請加上對應的燈號與狀態標籤：
                - 🔴 正在紮根：當任務難度低於實齡 {child_age}。
                - 🟡 穩定表現：當任務符合實齡 {child_age}。
                - 🟢 潛能爆發：當任務難度明顯高於實齡 {child_age}。
                
                ⚠️ 敘述格式請「嚴格依照」以下句型填空：
                「[燈號+狀態標籤]。此任務對應了幼教六大領域中的【(填入六大領域之一)領域】的指標，具體符合了發展常模中約【O-O 歲的 (填入具體能力，例如：精細動作操作 / 空間邏輯對應)】能力。對照 {child_name} 的實齡 {child_age}，在該領域的發展上(填入：表現穩定 / 需給予更多基礎引導 / 展現出優異的跨階潛能)。」

                第二段（能力說明）：
                請描述其當下操作的教育意義與未來發展路徑。
                敘述方式：請描述孩子如何透過當下的練習累積能力，以及這段經驗對於銜接下一個發展階段的重要性（例如：從平面轉向立體的基礎、從符號到具象的過渡等）。


                ### 🌱 【智慧鷹架引導】
                請運用多元鷹架支持策略，提供以下三個面向的引導建議。請嚴格使用五個井字號 (#####) 作為次標題：
                
                #####  啟發性對話
                提供 2 個開放式提問，協助老師引導孩子表達想法、邏輯或回顧解決問題的過程。
                
                #####  豐富探索環境
                提供 1 個「環境或材料」的調整建議，例如加入特定鬆散素材、工具或改變空間配置，來誘發孩子下一步的探索。
                
                #####  延伸挑戰
                提供 1 個設計目標更高層次的具體任務。
                ⚠️ 注意：請著重於「提升任務複雜度、改變遊戲規則、或跨領域結合（例如平面轉立體、單純操作轉為情境解謎）」，必須提供實質的認知或動作技能挑戰。

                ### 📝 【親師溝通筆記】
                給家長看的內容（約150字），請嚴格執行「三步溝通法」的語言轉換：
                1. **第一步：肯定亮點**：描述孩子在情境中「已經做到」的具體事實。
                2. **第二步：專業解讀（白話轉譯）**：⚠️ 嚴禁使用「落後、不會」或生硬的專業名詞（如萌芽期、紮根期）。請改用白話描述狀態，例如：「孩子正透過這些反覆的練習，一點一滴累積對...的掌控感」、「目前正處於蓄積能量的階段，透過觀察與嘗試來熟悉...」。
                3. **第三步：攜手建議**：提供一個家中隨手可做的遊戲化練習。
                
                保持日系溫暖感，適度使用🌸、🍃等符號。
                """
                
                response = model.generate_content([prompt, img])
                
                st.subheader("📋 專業觀察分析報告")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"系統忙碌中，請稍後再試。")
    else:
        st.warning("請填寫姓名、年齡並上傳照片喔！")

st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與探索中萌芽 🍃</p>", unsafe_allow_html=True)
