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
