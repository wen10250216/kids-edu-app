import streamlit as st

# 設定網頁風格
st.set_page_config(page_title="幼兒發展與教具分析系統", page_icon="🌱")

st.title("🌱 幼兒發展與教具互動分析系統")
st.markdown("### 結合 AI 視覺辨識，給予最溫暖的適性教學建議")
st.write("請上傳幼兒的作品或遊戲照片，系統將輔助您進行專業的發展評估與引導。")
st.divider()

# 建立輸入區塊
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📸 上傳幼兒作品或遊戲照片", type=["jpg", "png", "jpeg"])
with col2:
    child_age = st.text_input("🎈 輸入幼兒年齡 (例如：3歲6個月)")

st.divider()

# 按下按鈕後執行分析
if st.button("✨ 開始智慧分析", use_container_width=True):
    if uploaded_file is not None and child_age:
        with st.spinner("AI 正在以溫柔的視角觀察作品中..."):
            
            # 這裡暫時放入「模擬的分析結果」，讓您先看看排版效果！
            st.success("分析完成！請參考以下適性建議：")
            
            st.info("**👁️ 視覺觀察：**\n\n兩個精確的積木結構，利用對比色彩營造十字帶狀效果，並在下方弧形積木模擬蝴蝶結的造型。")
            st.warning("**📈 發展常模比對：**\n\n展現了3-4歲幼兒「象徵期」的特徵。能運用色彩分類與精確概念進行創作，把抽象積木賦予具體事物的意義，符合空間邏輯發展。")
            st.success("**🌟 現有能力評估：**\n\n孩子鍛鍊了出色的預先規劃能力與美感協調性。他不僅能精確對準積木邊角，更鍛鍊了從二維規律走向三維造型的穩定手眼協調，目前的自信心非常強健。")
            
            st.markdown("### 🌱 適性引導與拓展")
            st.markdown("- **提問引導：**『這兩個漂亮的禮盒是要送誰的驚喜呢？我們一起來猜猜看，裡面藏著什麼神奇的寶貝呀？』")
            st.markdown("- **玩法延伸：**邀請幼兒進行『大小比較』。可以鼓勵他嘗試做一個『更小』或『超級大』的禮物盒，加深空間量感的對比概念。")
    else:
        st.error("請記得上傳照片並輸入年齡喔！")
