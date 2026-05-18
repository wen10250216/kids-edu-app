import streamlit as st
import json

# 1. 設定網頁風格 (標題與說明)
st.title("🌱 幼兒發展與教具互動分析系統")
st.write("上傳幼兒的作品，讓 AI 輔助您進行專業的發展評估與教學引導。")

# 2. 建立輸入區塊
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📸 上傳幼兒作品照片", type=["jpg", "png", "jpeg"])
with col2:
    child_age = st.text_input("🎈 輸入幼兒年齡 (例如：3歲6個月)")

# 3. 按下按鈕後執行分析
if st.button("✨ 開始智能分析"):
    if uploaded_file is not None and child_age:
        with st.spinner("AI 正在以溫柔的視角觀察作品中..."):
            
            # --- 這裡會串接 Google Gemini API ---
            # (假設我們呼叫 API 後，收到了您截圖中的 JSON 字串：api_response_text)
            # api_response_text = call_gemini_api(uploaded_file, child_age) 
            
            # 4. 將 AI 給的 JSON 字串，轉換成 Python 可以讀懂的字典格式
            result_data = json.loads(api_response_text)
            
            # 5. 將資料變成漂亮的卡片排版 (呈現給使用者看)
            st.success("分析完成！請參考以下適性建議：")
            
            st.info(f"**👁️ 視覺觀察：**\n{result_data['視覺觀察']}")
            st.warning(f"**📈 發展常模比對：**\n{result_data['發展常模比對']}")
            st.success(f"**🌟 現有能力評估：**\n{result_data['現有能力評估']}")
            
            st.markdown("### 🌱 適性引導與拓展")
            for item in result_data['適性引導與拓展']:
                st.markdown(f"- {item}")
    else:
        st.error("請記得上傳照片並輸入年齡喔！")
