import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os

# 載入 Word 與 PDF 處理套件
try:
    from docx import Document
    from docx.shared import Inches, Cm
    from pypdf import PdfReader
except ImportError:
    st.error("❌ 系統偵測到缺漏套件，請在 requirements.txt 中新增：python-docx 與 pypdf")

# 1. 網頁風格設定 (日系療育風、馬卡龍色系)
st.set_page_config(page_title="幼兒學習發展分析系統", page_icon="🍃", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7fa !important; }
    h1 { color: #5d707a !important; text-align: center; font-weight: bold; font-family: 'Comic Sans MS', cursive, sans-serif; } 
    div.stButton > button:first-child {
        background-color: #ffccbc !important; color: #5d4037 !important;
        border-radius: 25px !important; border: 2px solid #ffb6a0 !important;
        font-weight: bold !important; width: 100% !important; padding: 10px !important;
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

# ---------------------------------------------------------
# ✨ 智慧 PDF 課綱快取引擎 (只有檔案更新時才會重新讀取)
# ---------------------------------------------------------
@st.cache_data
def load_curriculum_from_pdf(pdf_path):
    parsed_text = ""
    if os.path.exists(pdf_path):
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    parsed_text += text + "\n"
            return parsed_text
        except Exception as e:
            return f"PDF 解析出錯: {e}"
    return "尚未上傳官方課綱 PDF 檔案"

# 預先載入後台 PDF 資料
pdf_file_path = os.path.join("data", "curriculum.pdf")
curriculum_raw_text = load_curriculum_from_pdf(pdf_file_path)

# 3. 初始化 Session State
if 'generated_report' not in st.session_state:
    st.session_state.generated_report = None
if 'current_child' not in st.session_state:
    st.session_state.current_child = ""
if 'current_age' not in st.session_state:
    st.session_state.current_age = ""

# 4. Word 檔案生成函式 (動態模板引擎)
def build_word_file(child_name, child_age, report_text, uploaded_images, template_file=None):
    report_data = {"活動紀錄": "", "領域分析": "", "能力評估": "", "智慧鷹架": "", "親師溝通": ""}
    
    sections = report_text.split('### ')
    for sec in sections:
        if '活動紀錄' in sec: report_data["活動紀錄"] = sec.split('\n', 1)[-1].strip().replace('**', '')
        elif '發展領域分析' in sec: report_data["領域分析"] = sec.split('\n', 1)[-1].strip().replace('**', '')
        elif '現有能力評估' in sec: report_data["能力評估"] = sec.split('\n', 1)[-1].strip().replace('**', '')
        elif '智慧鷹架引導' in sec: report_data["智慧鷹架"] = sec.split('\n', 1)[-1].strip().replace('**', '')
        elif '親師溝通筆記' in sec: report_data["親師溝通"] = sec.split('\n', 1)[-1].strip().replace('**', '')

    if template_file is not None:
        template_file.seek(0)
        doc = Document(template_file)
        replacements = {
            "{{幼兒姓名}}": child_name, "{{幼兒年齡}}": child_age,
            "{{活動紀錄}}": report_data["活動紀錄"], "{{領域分析}}": report_data["領域分析"],
            "{{能力評估}}": report_data["能力評估"], "{{親師溝通}}": report_data["親師溝通"], "{{智慧鷹架}}": report_data["智慧鷹架"]
        }
        for paragraph in doc.paragraphs:
            for tag, text in replacements.items():
                if tag in paragraph.text: paragraph.text = paragraph.text.replace(tag, text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for tag, text in replacements.items():
                        if tag in cell.text: cell.text = cell.text.replace(tag, text)
                    if "{{照片歷程}}" in cell.text:
                        cell.text = cell.text.replace("{{照片歷程}}", "")
                        img_paragraph = cell.paragraphs[0]
                        if uploaded_images:
                            for file in uploaded_images:
                                file.seek(0)
                                img_bytes = file.read()
                                img_stream = io.BytesIO(img_bytes)
                                try:
                                    img = Image.open(img_stream)
                                    img_width, img_height = img.size
                                    img_stream.seek(0)
                                    run = img_paragraph.add_run()
                                    if img_width > img_height: run.add_picture(img_stream, width=Cm(8), height=Cm(6))
                                    else: run.add_picture(img_stream, width=Cm(6), height=Cm(8))
                                    run.add_text("  ") 
                                except: pass
    else:
        doc = Document()
        doc.add_heading(f'🍃 {child_name} 專業報告', level=1)
        doc.add_paragraph(f'☀️ 幼兒年齡：{child_age}')
        doc.add_paragraph('------------------------------------------------------------------')
        lines = report_text.split('\n')
        for line in lines:
            cleaned = line.strip()
            if not cleaned: continue
            if line.startswith('### '): doc.add_heading(cleaned.replace('### ', '').replace('**', ''), level=2)
            elif line.startswith('#### '): doc.add_heading(cleaned.replace('#### ', '').replace('**', ''), level=3)
            elif line.startswith('##### '): doc.add_heading(cleaned.replace('##### ', '').replace('**', ''), level=4)
            elif line.startswith('* ') or line.startswith('- '): doc.add_paragraph(cleaned[2:].replace('**', ''), style='List Bullet')
            else: doc.add_paragraph(cleaned.replace('**', ''))
                
        if uploaded_images:
            doc.add_page_break() 
            doc.add_heading('📝 (照片歷程紀錄)', level=2)
            img_paragraph = doc.add_paragraph() 
            for idx, file in enumerate(uploaded_images):
                file.seek(0)
                img_bytes = file.read()
                img_stream = io.BytesIO(img_bytes)
                try:
                    img = Image.open(img_stream)
                    img_width, img_height = img.size
                    img_stream.seek(0) 
                    run = img_paragraph.add_run()
                    if img_width > img_height: run.add_picture(img_stream, width=Cm(8), height=Cm(6))
                    else: run.add_picture(img_stream, width=Cm(6), height=Cm(8))
                    run.add_text("  ")
                except: doc.add_paragraph(f"[圖片載入失敗]")
                    
    output_stream = io.BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    return output_stream

# 5. 介面呈現
st.markdown("<h1>🍃 幼兒學習發展分析系統</h1>", unsafe_allow_html=True)
st.divider()

if os.path.exists(pdf_file_path):
    st.caption("🟢 系統狀態：後台官方課綱 PDF 檔案已智慧載入，全面啟動防幻覺精準對照。")
else:
    st.caption("🟡 系統狀態：未偵測到 data/curriculum.pdf，將切換為 AI 常規跨領域推論模式。")

col_name, col_age = st.columns(2)
with col_name: child_name = st.text_input("🖍️ 幼兒姓名 / 暱稱", placeholder="例如：雅雅")
with col_age: child_age = st.text_input("☀️ 幼兒年齡 (請精確輸入)", placeholder="例如：2歲5個月 或 6歲0個月")

teacher_notes = st.text_area("🖊️ 老師補充觀察 (為提升 AI 判定信心，建議補充以下資訊)", placeholder="1. 頻率：這是第一次發生、偶爾出現、還是穩定表現？\n2. 歷程：過程中是否失敗過？是否模仿同儕？\n3. 介入：老師有給予提示或動手幫忙嗎？\n4. 幼兒說的話：")

uploaded_files = st.file_uploader("🖼️ 1. 上傳觀察照片 (多張連拍歷程)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

with st.expander("💡 第一次使用自訂模板？點我查看【專屬標籤設定教學】🌸"):
    st.markdown("""
    為了讓系統精準填入您學校的格式，請在您電腦裡既有的 Word 空白紀錄表中，將需要讓系統代筆的地方，打上對應的「魔法標籤」（請連同大括號一起複製貼上喔！）：

    * 🖍️ **基本資訊**：`{{幼兒姓名}}`、`{{幼兒年齡}}`
    * 📝 **專業分析**：`{{活動紀錄}}`、`{{領域分析}}`、`{{能力評估}}`
    * 🌱 **支持策略**：`{{智慧鷹架}}`
    * 💌 **家長視角**：`{{親師溝通}}`
    * 🖼️ **動態相片牆**：請在表格的空白格子內填入 `{{照片歷程}}`，系統就會自動為您防變形縮放並整齊排版！
    
    > **🍃 實務小建議**：您可以先拿一份學校常用的空白表單，把上面這些標籤直接貼進對應的格子裡。以後每次只要上傳那份設定好的 Word 檔，系統就會變身為您的專屬行政小幫手！
    """)

template_file_upload = st.file_uploader("📄 2. 上傳學校既有 Word 紀錄表模板 (選填，不傳則用系統預設格式)", type=["docx"])

# 6. 執行分析
if st.button("🌟 生成專業觀察報告"):
    if uploaded_files and child_age and child_name:
        with st.spinner(f"正在透過證據權重模型與官方課綱 PDF 進行深度運算..."):
            try:
                media_contents = []
                
                prompt = f"""
                你是一套業界頂級的幼教發展評估可解釋性 AI (XAI) 系統。請基於「證據權重模型」綜合分析上傳的「系列照片 (動態歷程)」與以下資訊：
                - 幼兒姓名：{child_name}
                - 幼兒實齡：{child_age}
                - 教師補充觀察：{teacher_notes if teacher_notes else "無"}

                ⚠️ 【最高指導原則：教育部官方課綱絕對精確對照】
                系統後台已為你讀取了完整的教育部官方《幼兒園教保活動課程大綱》PDF 文本內容如下：
                ----- 後台官方課綱課文開始 -----
                {curriculum_raw_text[:80000]} 
                ----- 後台官方課綱課文結束 -----

                【指標解構與尋找指南】：
                官方課綱是由「領域能力」與「學習面向」交叉形成。
                請精確識別該活動符合哪一項「課程目標」，並根據幼兒的實齡 {child_age}，從上方的官方課綱課文中「一字不差」地提取出對應的【學習指標編碼與文字】（例如：身-幼-2-1-1 在穩定性及移動性動作中練習平衡）。
                絕對禁止發明、捏造任何課綱中不存在的指標與編碼！

                請依照以下結構輸出，語氣維持簡約療育風：

                ### 🔍 【活動紀錄與行為證據】
                客觀條列從照片與筆記中觀察到的「動態歷程證據」（如：嘗試堆疊、結構倒塌、自主更換底座、教師提供提示等）。不要在這裡下發展結論。

                ### 📊 【發展領域分析】
                請依據指南，精確定位並輸出符合的官方指標：
                - 符合課程目標：[請從 PDF 課文中找出對應的課程目標編碼與完整字句]
                - 具體對應學習指標：[請從 PDF 課文中精確找出符合幼兒年齡段的學習指標編碼與完整字句]

                ### ✨ 【現有能力評估】
                請綜合正反證據權重，給出評估結果（嚴禁標註數字或多餘列點）：

                【判定結果】：(請擇一輸出：⭐ 正在建立 / ⭐⭐ 穩定運用 / ⭐⭐⭐ 靈活遷移)
                
                【判定信心】：(請依據正反證據的強度，給出 0% - 100% 的估算值)
                
                【主要依據】：簡述判定成立的核心觀察。
                
                【尚缺證據】：指出若要提高信心分數，還需要觀察到什麼（如：不同情境的遷移、無提示下的獨立完成、長期穩定紀錄等，藉此引導老師下次補充）。

                第二段 (能力說明)：
                描述孩子如何透過當下的重複練習紮實地累積掌控感，以及這段經驗對於銜接下一個發展階段的重要性。

                ### 🌱 【智慧鷹架引導】
                基於 Vygotsky 的 ZPD 理論，嚴格使用五個井字號 (#####) 作為次標題，維持視覺層級：
                
                ##### ☀️ ZPD 下一步推估
                預測孩子下一個可以挑戰的具體能力目標。
                ##### ✨ 啟發性對話
                提供 1-2 個開放式提問。
                ##### 📈 探索環境擴充
                提供 1 個環境或素材的調整建議，以誘發 ZPD 的下一步行為。

                ### 🖍️ 【親師溝通筆記】
                給家長看的內容 (約150字)，請執行「三步溝通法」：肯定亮點、專業解讀 (白話轉譯且不用生硬術語)、攜手建議。整體保持日系手繪溫馨療育感。
                """
                
                media_contents.append(prompt)
                for file in uploaded_files:
                    img = Image.open(file)
                    media_contents.append(img)
                
                response = model.generate_content(media_contents)
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
    
    word_data = build_word_file(
        st.session_state.current_child,
        st.session_state.current_age,
        st.session_state.generated_report,
        uploaded_files,
        template_file_upload
    )
    
    st.download_button(
        label=f"💾 匯出 {st.session_state.current_child} 的 Word 報告",
        data=word_data,
        file_name=f"{st.session_state.current_child}_觀察紀錄表.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與探索中萌芽 🍃</p>", unsafe_allow_html=True)
