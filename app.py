from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
from PIL import Image

def parse_report_sections(report_text):
    """
    將 AI 回應的報告文字，依照關鍵標題分割成區塊字典。
    假設 report_text 格式如下（各段以「標題：」開頭）：
        活動紀錄：xxx
        發展領域分析：xxx
        現有能力評估：xxx
        親師溝通筆記：xxx
        智慧鷹架引導：xxx
    """
    sections = {}
    current_key = None
    for line in report_text.split('\n'):
        for key in ["活動紀錄", "發展領域分析", "現有能力評估", "親師溝通筆記", "智慧鷹架引導"]:
            if line.startswith(key + "："):
                current_key = key
                sections[current_key] = line[len(key)+1:]
                break
        else:
            if current_key:
                # 若不是新標題行，則追加到現有區塊（保留換行）
                sections[current_key] += "\n" + line
    # 確保所有 key 都存在（空字串也補上）
    for key in ["活動紀錄", "發展領域分析", "現有能力評估", "親師溝通筆記", "智慧鷹架引導"]:
        sections.setdefault(key, "")
    return sections

def build_word_file(child_name, child_age, report_text, uploaded_images, template_file=None):
    import io

    # 解析 AI 報告的各個區塊內容，轉成字典備用
    report_data = parse_report_sections(report_text)

    if template_file is not None:
        # 【智慧自訂模板模式】
        template_file.seek(0)
        doc = Document(template_file)

        # 1. 定義要替換的文字標籤對照表
        replacements = {
            "{{幼兒姓名}}": child_name,
            "{{幼兒年齡}}": child_age,
            "{{活動紀錄}}": report_data.get("活動紀錄", ""),
            "{{領域分析}}": report_data.get("發展領域分析", ""),
            "{{能力評估}}": report_data.get("現有能力評估", ""),
            "{{親師溝通}}": report_data.get("親師溝通筆記", ""),
            "{{智慧鷹架}}": report_data.get("智慧鷹架引導", "")
        }

        # 2. 智慧搜尋並替換一般段落中的文字
        for paragraph in doc.paragraphs:
            for tag, text in replacements.items():
                if tag in paragraph.text:
                    paragraph.text = paragraph.text.replace(tag, text)

        # 3. 智慧搜尋並替換「表格格子」中的文字
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    # 替換表格內的文字標籤
                    for tag, text in replacements.items():
                        if tag in cell.text:
                            cell.text = cell.text.replace(tag, text)

                    # 4. 智慧照片投放
                    if "{{照片歷程}}" in cell.text:
                        cell.text = cell.text.replace("{{照片歷程}}", "")   # 清空標籤
                        # 取第一個段落（保證存在）
                        img_paragraph = cell.paragraphs
                        if uploaded_images:
                            for file in uploaded_images:
                                file.seek(0)
                                img_bytes = file.read()
                                img_stream = io.BytesIO(img_bytes)
                                try:
                                    img = Image.open(img_stream)
                                    img_width, img_height = img.size
                                    img_stream.seek(0)  # 重設串流位置給 add_picture 讀取

                                    run = img_paragraph.add_run()
                                    # 橫直式防變形邏輯
                                    if img_width > img_height:
                                        run.add_picture(img_stream, width=Cm(8), height=Cm(6))
                                    else:
                                        run.add_picture(img_stream, width=Cm(6), height=Cm(8))
                                    run.add_text("  ")  # 照片間距
                                except Exception:
                                    pass   # 忽略無法讀取的圖片

    else:
        # 【系統預設常規模式】 – 建立一份標準的觀察紀錄文件
        doc = Document()

        # 設定預設字型
        style = doc.styles['Normal']
        font = style.font
        font.name = '微軟正黑體'
        font.size = Pt(12)

        # 標題
        title = doc.add_heading('幼兒觀察紀錄', level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 基本資料區
        info = doc.add_paragraph()
        info.add_run('幼兒姓名：').bold = True
        info.add_run(child_name)
        info.add_run('\t幼兒年齡：').bold = True
        info.add_run(child_age)

        doc.add_paragraph()  # 空行

        # 五個區塊的標題與內容
        section_order = ["活動紀錄", "發展領域分析", "現有能力評估", "親師溝通筆記", "智慧鷹架引導"]
        for sec_name in section_order:
            heading = doc.add_heading(sec_name, level=2)
            content = report_data.get(sec_name, "")
            if content:
                doc.add_paragraph(content)
            else:
                doc.add_paragraph("（無資料）")

        # 照片區（若使用者有上傳照片，則加在最後）
        if uploaded_images:
            doc.add_paragraph()  # 空行
            photo_heading = doc.add_heading('歷程照片', level=2)
            for file in uploaded_images:
                file.seek(0)
                img_bytes = file.read()
                img_stream = io.BytesIO(img_bytes)
                try:
                    img = Image.open(img_stream)
                    img_width, img_height = img.size
                    img_stream.seek(0)
                    # 照片單獨一個段落
                    para = doc.add_paragraph()
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = para.add_run()
                    if img_width > img_height:
                        run.add_picture(img_stream, width=Cm(12), height=Cm(9))
                    else:
                        run.add_picture(img_stream, width=Cm(9), height=Cm(12))
                except Exception:
                    # 若無法讀取則略過
                    pass

    output_stream = io.BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    return output_stream
