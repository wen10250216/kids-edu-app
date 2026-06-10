import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os
import pandas as pd
from datetime import datetime

# 載入 Word 與 PDF、視覺化處理套件
try:
    from docx import Document
    from docx.shared import Inches, Cm
    from pypdf import PdfReader
    import plotly.express as px
except ImportError:
    st.error("❌ 雲端套件正在安裝中，請稍候一分鐘並重新整理網頁。")

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

# 2. 安全讀取 Gemini API Key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("❌ 尚未在 Streamlit 後台設定 GEMINI_API_KEY")

try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
    model = genai.GenerativeModel(target_model)
except:
    model = genai.GenerativeModel('gemini-1.5-flash')

# 3. 智慧 PDF 課綱快取引擎
@st.cache_data
def load_curriculum_from_pdf(pdf_path):
    parsed_text = ""
    if os.path.exists(pdf_path):
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                text = page.extract_text()
                if text: parsed_text += text + "\n"
            return parsed_text
        except Exception as e: return f"PDF 解析出錯: {e}"
    return "尚未上傳官方課綱 PDF 檔案"

pdf_file_path = os.path.join("data", "curriculum.pdf")
curriculum_raw_text = load_curriculum_from_pdf(pdf_file_path)

# 初始化 Session State
if 'generated_report' not in st.session_state: st.session_state.generated_report = None
if 'current_child' not in st.session_state: st.session_state.current_child = ""
if 'current_age' not in st.session_state: st.session_state.current_age = ""
if 'session_history' not in st.session_state: st.session_state.session_history = pd.DataFrame(columns=['日期', '幼兒姓名', '幼兒年齡', '對應領域', '學習指標', '現有能力評估', '親師溝通'])

# 4. Word 檔案生成函式
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

# 5. 側邊欄：純檔案式大數據歷史載入區（老師絕對學得會！）
with st.sidebar:
    st.markdown("### 📊 班級歷史紀錄檔案袋")
    st.write("本系統不留存任何幼兒隱私至雲端，所有成長數據皆存在您電腦本機中。")
    
    # 讓老師直接拖放舊的 CSV 紀錄檔進來
    history_file = st.file_uploader("📂 請上傳您個人的歷史紀錄舊檔案 (.csv)", type=["csv"], help="初次使用免傳，第二次使用時將上次下載的檔案傳上來即可回復所有圖表！")
    
    # 智慧歷史檔案整合管線
    if history_file is not None:
        try:
            uploaded_df = pd.read_csv(history_file)
            # 防呆檢查欄位是否符合格式
            required_cols = ['日期', '幼兒姓名', '幼兒年齡', '對應領域', '學習指標', '現有能力評估', '親師溝通']
            if all(col in uploaded_df.columns for col in required_cols):
                st.session_state.session_history = uploaded_df
                st.sidebar.success("🟢 班級歷史紀錄已智慧同步！")
            else:
                st.sidebar.error("❌ 上傳的檔案格式不符，請確認是從本系統下載的檔案。")
        except Exception as e:
            st.sidebar.error(f"檔案讀取失敗: {e}")

    # 智慧盲區動態診斷看板
    if not st.session_state.session_history.empty:
        st.markdown("---")
        st.markdown("### 📊 班級整體觀測平衡診斷")
        df_history = st.session_state.session_history
        
        domain_counts = df_history['對應領域'].value_counts().to_dict()
        all_domains = ["認知領域", "身體動作與健康領域", "語文領域", "社會領域", "情緒領域", "美感領域"]
        chart_data = {dom: domain_counts.get(dom, 0) for dom in all_domains}
        
        plot_df = pd.DataFrame(list(chart_data.items()), columns=['領域', '觀測次數'])
        fig = px.line_polar(plot_df, r='觀測次數', theta='領域', line_close=True, color_discrete_sequence=['#ffccbc'])
        fig.update_traces(fill='adjacent')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, side='counter-clockwise')), showlegend=False, margin=dict(l=20, r=20, t=20, b=20), height=200)
        st.plotly_chart(fig, use_container_width=True)
        
        blind_spots = [dom for dom, count in chart_data.items() if count < 3]
        if blind_spots:
            st.warning(f"💡 觀測盲區警示：班級在『{', '.join(blind_spots)}』的數據累積較少（不足3次），建議近期可調整觀察視角喔！")
        else:
            st.success("🟢 班級觀測非常均衡，六大領域皆有紮實記錄！")

# 6. 主畫面介面呈現 (大標題)
st.markdown("<h1>🍃 幼兒學習發展分析系統</h1>", unsafe_allow_html=True)
st.divider()

# 雙分頁系統
tab_record, tab_chart = st.tabs(["📝 新增動態觀察", "📈 幼兒個人成長看板"])

# ---------------------------------------------------------
# 分頁一：新增與生成紀錄表
# ---------------------------------------------------------
with tab_record:
    if os.path.exists(pdf_file_path):
        st.caption("🟢 系統狀態：後台官方課綱 PDF 檔案已智慧載入，全面啟動防幻覺精準對照。")
    else:
        st.caption("🟡 系統狀態：未偵測到 data/curriculum.pdf，將切換為 AI 常規跨領域推論模式。")

    col_name, col_age = st.columns(2)
    with col_name: child_name = st.text_input("🖍️ 幼兒姓名 / 暱稱", placeholder="例如：雅雅")
    with col_age: child_age = st.text_input("☀️ 幼兒年齡 (請精確輸入)", placeholder="例如：2歲5個月 或 6歲0個月")

    teacher_notes = st.text_area("🖊️ 老師補充觀察 (為提升 AI 判定信心，建議補充以下資訊)", placeholder="1. 頻率：這是第一次發生、偶爾出現、還是穩定表現？\n2. 歷程：過程中是否失敗過？是否模仿同儕？\n3. 介入：老師有給予提示或動手幫忙嗎？\n4. 幼兒說的話：", key="input_notes")

    uploaded_files = st.file_uploader("🖼️ 1. 上傳觀察照片 (多張連拍歷程)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    with st.expander("💡 第一次使用？點我查看【自訂模板標籤】與【本機自動歸檔教學】🌸"):
        st.markdown("""
        為了讓系統完美接軌您個人的行政節奏，請花 1 分鐘參考以下現場實務設定：
        
        ### 📋 一、 學校既有 Word 表格標籤設定
        * 🖍️ **基本資訊**：`{{幼兒姓名}}`、`{{幼兒年齡}}`
        * 📝 **專業分析**：`{{活動紀錄}}`、`{{領域分析}}`、`{{能力評估}}`
        * 🌱 **支持策略**：`{{智慧鷹架}}`
        * 💌 **家長視角**：`{{親師溝通}}`
        * 🖼️ **動態相片牆**：`{{照片歷程}}`
        
        > 💡 **老師的彈性自訂小技巧**：如果您學校的表格很精簡，只需要「姓名」和「親師溝通」，您在 Word 裡就**只要貼這兩個標籤就好**！其他沒貼的標籤系統會自動忽略，完全不會影響運作。
        
        ---
        ### 📂 二、 獨家大絕招：網頁按下一鍵，自動飛進電腦指定資料夾！
        1. **建資料夾**：先在您電腦桌面新增一個專屬資料夾（如：`2026學期幼兒觀察紀錄`）。
        2. **打開設定**：打開 Chrome 瀏覽器 ➜ 點擊右上角「三個點」 ➜ 選擇 **「設定」**。
        3. **變更路徑**：點選左側的 **「下載」**：
           * 將「位置」更改為您剛剛在桌面建好的那個資料夾。
           * 將「下載每個檔案前先詢問儲存位置」**關閉**。
        """)

    template_file_upload = st.file_uploader("📄 2. 上傳學校既有 Word 紀錄表模板 (選填，不傳則用系統預設格式)", type=["docx"])

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

                    ⚠️ 【最高指導原則：教育部官方課綱絕對精確對照與核心欄位精準輸出】
                    系統後台已為你讀取了完整的教育部官方《幼兒園教保活動課程大綱》PDF 文本內容如下：
                    {curriculum_raw_text[:60000]} 

                    請嚴格依據幼兒的實齡 {child_age} 一字不差地提取指標。
                    請嚴格遵守在特定區塊標註【核心領域標籤: 領域名稱】與【核心指標標籤: 指標名稱】。

                    請依照以下結構輸出，語氣維持簡約療育風：

                    ### 🔍 【活動紀錄與行為證據】
                    客觀條列動態歷程證據。

                    ### 📊 【發展領域分析】
                    【核心領域標籤: (請從 PDF 課文中精確填入其一：認知領域 / 身體動作與健康領域 / 語文領域 / 社會領域 / 情緒領域 / 美感領域)】
                    【核心指標標籤: (請精確寫出對應指標與編碼，例如：身-幼-2-1-1 在穩定性及移動性動作中練習平衡)】
                    - 符合課程目標：[課程目標完整字句]
                    - 具體對應學習指標：[學習指標完整字句]

                    ### ✨ 【現有能力評估】
                    【判定結果】：(請擇一輸出：⭐ 正在建立 / ⭐⭐ 穩定運用 / ⭐⭐⭐ 靈活遷移)
                    【判定信心】：(請給出 0% - 100% 的估算值)
                    【主要依據】：簡述判定成立的核心觀察。
                    【尚缺證據】：指出若要提高信心分數還需要觀察到什麼。

                    第二段 (能力說明)：
                    描述對應發展常模的深層教育意義。

                    ### 🌱 【智慧鷹架引導】
                    ##### ☀️ ZPD 下一步推估
                    ##### ✨ 啟發性對話
                    ##### 📈 探索環境擴充

                    ### 🖍️ 【親師溝通筆記】
                    給家長看的內容 (約150字)，請執行「三步溝通法」保持手繪療育感。
                    """
                    media_contents.append(prompt)
                    for file in uploaded_files:
                        img = Image.open(file)
                        media_contents.append(img)
                    
                    response = model.generate_content(media_contents)
                    report_text = response.text
                    st.session_state.generated_report = report_text
                    st.session_state.current_child = child_name
                    st.session_state.current_age = child_age
                    
                    # 背景自動更新 Session 內部的 DataFrame
                    extracted_domain = "未歸類"
                    extracted_indicator = "未識別"
                    if "【核心領域標籤:" in report_text: extracted_domain = report_text.split("【核心領域標籤:")[1].split("】")[0].strip()
                    if "【核心指標標籤:" in report_text: extracted_indicator = report_text.split("【核心指標標籤:")[1].split("】")[0].strip()
                    
                    eval_summary = "⭐ 正在建立"
                    if "⭐⭐⭐ 靈活遷移" in report_text: eval_summary = "⭐⭐⭐ 靈活遷移"
                    elif "⭐⭐ 穩定運用" in report_text: eval_summary = "⭐⭐ 穩定運用"
                    
                    note_summary = report_text.split('### 🖍️ ')[-1].split('\n', 1)[-1].strip() if '### 🖍️ ' in report_text else "無"
                    
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    new_row = pd.DataFrame([{
                        '日期': today_str, '幼兒姓名': child_name, '幼兒年齡': child_age,
                        '對應領域': extracted_domain, '學習指標': extracted_indicator,
                        '現有能力評估': eval_summary, '親師溝通': note_summary[:100] + "..."
                    }])
                    st.session_state.session_history = pd.concat([st.session_state.session_history, new_row], ignore_index=True)
                    st.toast("🎉 本次觀察已暫存，請記得在下方下載更新歷史檔案喔！", icon="📝")
                        
                except Exception as e:
                    st.error(f"系統發生錯誤，錯誤訊息：{e}")
        else:
            st.warning("請填寫姓名、年齡並至少上傳一張照片喔！")

    if st.session_state.generated_report:
        st.subheader("📋 專業觀察分析報告")
        st.markdown(st.session_state.generated_report)
        st.divider()
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            word_data = build_word_file(st.session_state.current_child, st.session_state.current_age, st.session_state.generated_report, uploaded_files, template_file_upload)
            st.download_button(label=f"doc 匯出 {st.session_state.current_child} 的 Word 報告", data=word_data, file_name=f"{st.session_state.current_child}_觀察紀錄表.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        with col_btn2:
            # ✨ 提供老師下載最新融合後 CSV 的功能
            csv_buffer = io.StringIO()
            st.session_state.session_history.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📈 下載更新後的班級歷史紀錄 (.csv)",
                data=csv_buffer.getvalue(),
                file_name=f"班級學習歷程紀錄表_{datetime.now().strftime('%m%d')}.csv",
                mime="text/csv"
            )

# ---------------------------------------------------------
# 分頁二：智慧讀取與幼兒個人成長圖表分析 (從快取 DataFrame 讀取)
# ---------------------------------------------------------
with tab_chart:
    st.markdown("### 📈 幼兒長期發展成長圖表")
    
    if not st.session_state.session_history.empty:
        df_history = st.session_state.session_history
        unique_children = df_history['幼兒姓名'].unique().tolist()
        selected_child = st.selectbox("🖍️ 請選擇要調閱成長圖表的幼兒姓名：", unique_children)
        
        if selected_child:
            df_child = df_history[df_history['幼兒姓名'] == selected_child].sort_values(by='日期')
            st.markdown(f"#### 🍃 {selected_child} 的縱向能力發展軌跡")
            st.write(f"📊 目前已在檔案袋中，累積了 **{len(df_child)}** 筆縱向發展觀測事實。")
            
            status_map = {"⭐ 正在建立": 1, "⭐⭐ 穩定運用": 2, "⭐⭐⭐ 靈活遷移": 3}
            df_child['能力分數'] = df_child['現有能力評估'].map(status_map).fillna(1)
            
            fig_line = px.line(
                df_child, x='日期', y='能力分數', color='對應領域',
                markers=True, text='現有能力評估',
                title=f"📈 {selected_child} 的跨領域能力演進圖 (縱向學習歷程)",
                color_discrete_sequence=['#ffccbc', '#b2dfdb', '#ffe082', '#c5cae9', '#e1bee7', '#ffcdd2']
            )
            fig_line.update_yaxes(tickvals=[1, 2, 3], ticktext=["正在建立", "穩定運用", "靈活遷移"], range=[0.5, 3.5])
            fig_line.update_traces(textposition="top center")
            fig_line.update_layout(hovermode="x unified")
            st.plotly_chart(fig_line, use_container_width=True)
            
            st.markdown("#### 📜 歷史觀察足跡摘要")
            st.dataframe(df_child[['日期', '幼兒年齡', '對應領域', '學習指標', '現有能力評估', '親師溝通']], use_container_width=True, hide_index=True)
    else:
        st.info("💡 目前歷史資料庫為空。請先於左側上傳您的 `.csv` 歷史紀錄檔案，或是直接在隔壁分頁新增觀察，系統即可即時幫您解鎖『縱向成長看板』功能喔！")

st.markdown("<br><p style='text-align: center; color: #b0bec5;'>🍃 陪伴孩子在愛與探索中萌芽 🍃</p>", unsafe_allow_html=True)
