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
                請將評估邏輯「無痕」融入流暢、溫暖的段落中，絕對不要標註 1. 2. 3.。
                ⚠️ 嚴禁使用「依據常模」等生硬術語，請代入專業老師的觀察口吻。

                請執行以下「動態領域比對邏輯」：
                1. 識別活動領域與難度：請自動判斷照片中的活動屬於哪個領域（如：精細動作、大肌肉協調、美感創作、視覺空間等），並根據該領域的發展指標定位其難度。
                   - 例：繪畫（從塗鴉到具象符號）、運動（從單腳站立到跨越障礙）、拼圖（從少片數到複雜空間構成）。
                2. 實齡動態比對：將辨識出的活動難度與幼兒實齡 {child_age} 進行對比。
                
                【描述策略】：
                - 若「活動難度」明顯低於「幼兒實齡」：描述為「基礎經驗的深耕」。肯定其穩定度與耐心，並指出這是在為更高階的複雜技能（如：複雜圖形繪製、動態平衡）紮根。
                - 若「活動難度」明顯高於「幼兒實齡」：描述為「潛能的跨階展現」。肯定其超齡的專注力或協調性，描述為該領域發展的卓越亮點。
                - 若任務符合實齡：描述為「發展步調的穩健與自信」。肯定其游刃有餘的操作，展現了該年紀應有的發展里程碑。

                無論表現如何，請將焦點放在「孩子當下的狀態」對未來發展的長遠意義，嚴禁使用負面詞彙。

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
