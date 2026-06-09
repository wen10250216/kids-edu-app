import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 載入 Word 處理套件
try:
    from docx import Document
    from docx.shared import Inches
except ImportError:
    st.error("❌ 系統偵測到缺漏套件，請在 requirements.txt 中新增一行：python-docx")

# 1. 網頁風格設定 (將圖案更換為療育手繪風)
st.set_page_config(page_title="幼兒學習發展分析系統", page_icon="🍃", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7fa !important; }
    h1 { color: #5d707a !important; text-align: center; font-weight: bold; font-family: 'Comic Sans MS', cursive, sans-serif; } /* 字體改為較療育的手寫感 */
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
    .stMarkdown { line-height: 1.8; color: #37474f; font-family: 'Verdana', sans-serif; }
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

# 3. 初始化 Session State
if 'generated_report' not in st.session_state:
    st.session_state.generated_report = None
if 'current_child' not in st.session_state:
    st.session_state.current_child = ""
if 'current_age' not in st.session_state:
    st.session_state.current_age = ""

# 4. Word 檔案生成函式 (更換圖案為簡約手繪風)
def build_word_file(child_name, child_age, report_text, uploaded_images):
    doc = Document()
    
    # 文件標題更換為簡約手繪風
    doc.add_heading(f'🍃 {child_name} 專業報告', level=1)
    doc.add_paragraph(f'☀️ 幼兒年齡：{child_age}')
    doc.add_paragraph('------------------------------------------------------------------')
    
    # 逐行解析 Markdown 並轉換為 Word 格式
    lines = report_text.split('\n')
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        
        # 標題層級轉譯
        if line.startswith('### '):
            doc.add_heading(cleaned.replace('### ', '').replace('**', ''), level=2)
        elif line.startswith('#### '):
            doc.add_heading(cleaned.replace('#### ', '').replace('**', ''), level=3)
        elif line.startswith('##### '):
            doc.add_heading(cleaned.replace('##### ', '').replace('**', ''), level=4)
        # 列表樣式轉譯
        elif line.startswith('* ') or line.startswith('- '):
            doc.add_paragraph(cleaned[2:].replace('**', ''), style='List Bullet')
        else:
            doc.add_paragraph(cleaned.replace('**', ''))
            
    # 自動排版照片，標題更換為簡約手繪風
    if uploaded_images:
        doc.add_paragraph('\n')
        doc.add_heading('📝 (照片歷程紀錄)', level=2)
        for idx, file in enumerate(uploaded_images):
            file.seek(0)
            img_bytes = file.read()
            img_stream = io.BytesIO(img_bytes)
            try:
                doc.add_paragraph(f'【動態歷程紀錄 照片 {idx+1}】')
                doc.add_picture(img_stream, width=Inches(4.5)) 
                doc.add_paragraph() 
            except Exception as e:
                doc.add_paragraph(f"[圖片 {idx+1} 載入失敗: {e}]")
                
    output_stream = io.BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    return output_stream

# 5. 介面呈現 (更換小圖案為手繪療育風)
st.markdown("<h1>🍃 幼兒學習發展分析系統</h1>", unsafe_allow_html=True)
st.divider()

col_name, col_age = st.columns(2)
with col_name:
    child_name = st.text_input("🖍️ 幼兒姓名 / 暱稱", placeholder="例如：雅雅")
with col_age:
    child_age = st.text_input("☀️ 幼兒年齡", placeholder="例如：5歲9個月")

teacher_notes = st.text_area("🖊️ 老師補充觀察 (選填)", placeholder="描述孩子在過程中的口語、試錯歷程或與同伴的互動。")

uploaded_files = st.file_uploader("🖼️ 上傳觀察照片 (多張連拍歷程)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# 6. 執行分析
if st.button("🌟 生成專業觀察報告"):
    if uploaded_files and child_age and child_name:
        with st.spinner(f"正在為 {child_name} 綜合分析活動歷程..."):
            try:
                media_contents = []
                
                # 核心分析指令：將小圖案更換為療育手繪風描述，維持 colored status dots
                prompt = f"""
                你是一套專為專業發展評估設計的 AI 系統，具備溫暖療育的手繪風格筆觸。請綜合分析上傳的「系列照片 (動態歷程)」與以下資訊，產出一份具備療育與專業感的報告：
                - 幼兒姓名：{child_name}
                - 幼兒年齡：{child_age}
                - 老師補充：{teacher_notes if teacher_notes else "無"}

                ⚠️ 【最高指導原則：嚴禁臆測 facts】
                1. 嚴禁使用「專注、細心、耐心」等描述心理狀態的詞彙，除非老師筆記中有具體提及。
                2. 嚴禁描述與能力評估無關的衣著顏色或環境背景。請直接描述【能力展現事實】。
                3. 報告開頭第一句話請嚴格符合以下句型：這是一份關於 {child_name} 的專業發展評估報告，供老師內部參考。

                請依照以下結構輸出，將圖案與描述都轉換為簡約療育風：

                ### 📝 【{child_name} 的活動紀錄】
                綜合系列照片與老師補充，描述活動中的能力展現與解決問題的歷程。請用細膩的文字勾勒出孩子的操作細節。

                ### 📊 【發展領域分析】
                精確論述孩子行為所展現出的具體能力指標，對應教育部幼教六大領域，以簡約專業的風格論述。

                ### ✨ 【現有能力評估】
                請將評估邏輯分為「兩段」清晰的文字敘述，嚴禁標註數字或列點，請保持療育感。

                第一段 (能力判斷)：
                請直接將辨識出的活動精準對應「六大領域」與「發展常模」，並在開頭加上對應的燈號與狀態標籤：
                - 🔴 正在紮根：任務難度低於實齡。
                - 🟡 穩定表現：任務難度符合實齡。
                - 🟢 潛能爆發：任務難度明顯高於實齡。
                敘述方式需嚴格遵守白話與狀態描述的原則。

                第二段 (能力說明)：
                描述孩子如何透過當下的重複練習紮實地累積掌控感，以及這段經驗對於銜接下一個發展階段的重要性 (例如平面轉立體、單純操作轉為情境應用等)。

                ### 🌱 【智慧鷹架引導】
                請運用療育風的鷹架支持策略，為老師提供以下三個面向的引導建議。請嚴格使用五個井字號 (#####) 作為次標題，維持視覺層級：
                
                ##### ☀️ 啟發性對話
                提供 1-2 個開放式提問。
                
                ##### ✨ 豐富探索環境
                提供 1 個設計目標更高層次的延伸素材投放或環境調整建議。
                
                ##### 📈 延伸挑戰
                提供 1 個設計目標更高層次的具體任務，嚴禁只建議「邀請朋友一起玩」。

                ### 🖍️ 【親師溝通筆記】
                給家長看的內容 (約150字)，請嚴格執行「三步溝通法」的語言轉換，請保持日系手繪療育感：
                - 第一步：肯定亮點：描述孩子在情境中「已經做到」的微小事实。
                - 第二步：專業解讀 (白話轉譯)：嚴禁使用落後、慢、不會或生硬術語 (如萌芽、紮根)，請改用簡約療育描述狀態 (例如：一點一滴累積掌控感、處於蓄積能量階段)。
                - 第三步：攜手建議：提供一個家中隨手可做的遊戲化練習。
                
                整體保持溫暖疗育感，適度使用🌸、🍃等符號。
                """
                
                media_contents.append(prompt)
                for file in uploaded_files:
                    img = Image.open(file)
                    media_contents.append(img)
                
                response = model.generate_content(media_contents)
                
                # 將結果存入 Session State
                st.session_state.generated_report = response.text
                st.session_state.current_child = child_name
                st.session_state.current_age = child_age
                
            except Exception as e:
                st.error(f"系統發生錯誤，可能是照片過大或系統忙碌中，請稍後再試。錯誤訊息：{e}")
    else:
        st.warning("請填寫姓名、年齡並至少上傳一張照片喔！")

# 7. 渲染報告與提供下載按鈕
if st.session_state.generated_report:
    st.subheader("📋 專業觀察分析報告")
    st.markdown(st.session_state.generated_report)
    
    st.divider()
    
    # 背景生成 Word 檔案流
    word_data = build_word_file(
        st.session_state.current_child,
        st.session_state.current_age,
        st.session_state.generated_report,
        uploaded_files
    )
    
    # 下載按鈕更換圖案為簡約手繪風
    st.download_button(
        label=f"💾 下載 Word 報告 (內含照片歷程)",
        data=word_data,
        file_name=f"{st.session_state.current_child}_專業發展評估報告.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與探索中萌芽 🍃</p>", unsafe_allow_html=True)
