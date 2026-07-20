import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import io

# --- ตั้งค่าหน้าจอและ CSS สำหรับความสวยงาม ---
st.set_page_config(page_title="Financial Intelligence 2026", layout="wide")

# ใส่ CSS เข้าไปเพื่อแต่ง Background และปุ่ม 3 มิติ
st.markdown("""
    <style>
    /* Background ของทั้งหน้าจอ */
    .stApp {
        background: linear-gradient(135deg, #f6f8f9 0%, #e5ebee 100%);
        background-image: url('https://www.transparenttextures.com/patterns/diagmonds-light.png');
    }
    
    /* แต่ง Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }

    /* แต่ง Header ของ Sidebar */
    .css-17lntkn {
        color: #1f77b4;
        font-weight: bold;
    }

    /* ปุ่ม 3 มิติ (ปุ่มบันทึก, อัปเดต, พิมพ์) */
    div.stButton > button, div.stDownloadButton > button {
        color: white !important;
        border: none;
        padding: 12px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        /* เอฟเฟกต์ 3 มิติ */
        background-color: #34a853; /* สีหลัก */
        box-shadow: 0 4px #2e8651; 
        transition: all 0.1s ease-in-out;
    }
    
    /* เอฟเฟกต์ตอนกด (ปุ่มยุบลง) */
    div.stButton > button:active, div.stDownloadButton > button:active {
        box-shadow: 0 2px #2e8651;
        transform: translateY(2px);
    }
    
    /* เปลี่ยนสีปุ่มอัปเดตให้ต่างออกไป */
    div[data-testid="stVerticalBlock"] > div > div > div > div[data-testid="stHorizontalBlock"] > div:first-child > div > div > button {
        background-color: #ff9800; /* สีส้ม */
        box-shadow: 0 4px #e68a00;
    }
    div[data-testid="stVerticalBlock"] > div > div > div > div[data-testid="stHorizontalBlock"] > div:first-child > div > div > button:active {
        box-shadow: 0 2px #e68a00;
    }

     /* เปลี่ยนสีปุ่มพิมพ์ */
    div.stDownloadButton > button {
        background-color: #4285f4; /* สีฟ้า */
        box-shadow: 0 4px #3367d6;
    }
    div.stDownloadButton > button:active {
        box-shadow: 0 2px #3367d6;
    }

    /* กรอบของ Data Editor */
    div[data-testid="stDataEditor"] {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["วันที่", "รายการ", "บัญชี", "รายรับ", "รายจ่าย"]).to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

def get_data():
    return pd.read_csv(DATA_FILE)

st.title("📊 Financial Intelligence 2026")

# 1. ฟอร์มบันทึก (พร้อมปุ่ม 3 มิติ)
with st.sidebar.form("input_form", clear_on_submit=True):
    st.header("➕ บันทึกรายการ")
    date_input = st.date_input("วันที่", datetime.now())
    item = st.text_input("รายการ")
    account = st.selectbox("บัญชี", ["ธกส (เจ้านาย)", "กสิกรไทย (เจ้านาย)", "กสิกรไทย (น้องจอย)", "เงินสด"])
    amount_type = st.radio("ประเภท", ["รายรับ", "รายจ่าย"])
    amount = st.number_input("จำนวนเงิน", min_value=0.0, step=1.0)
    if st.form_submit_button("💾 บันทึก"): # ปุ่ม 3 มิติ
        new_df = pd.DataFrame([{"วันที่": date_input, "รายการ": item, "บัญชี": account, 
                               "รายรับ": amount if amount_type == "รายรับ" else 0, 
                               "รายจ่าย": amount if amount_type == "รายจ่าย" else 0}])
        new_df.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
        st.rerun()

# 2. จัดการข้อมูล และรีเฟรชข้อมูลล่าสุด
df = get_data() # ดึงข้อมูลล่าสุดจากไฟล์ใหม่เสมอ
st.subheader("📋 รายการทั้งหมด (แก้ไขได้)")
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("🔄 อัปเดตและบันทึกข้อมูลใหม่"): 
    edited_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
    st.success("อัปเดตข้อมูลเรียบร้อย!")
    st.rerun() # สั่งให้หน้าจอรีเฟรชใหม่ทันทีหลังจากกดอัปเดต

# 3. สรุปยอด
st.subheader("💰 สรุปยอดคงเหลือ")
df = get_data()
grouped = df.groupby('บัญชี')[['รายรับ', 'รายจ่าย']].sum()
grouped['ยอดคงเหลือ'] = grouped['รายรับ'] - grouped['รายจ่าย']
summary = grouped.reset_index()

num_accounts = len(summary)
cols = st.columns(num_accounts)
for i, row in summary.iterrows():
    cols[i].metric(label=row['บัญชี'], value=f"{row['ยอดคงเหลือ']:,.2f}")

# 4. สั่งพิมพ์ (ปุ่มดาวน์โหลด 3 มิติ)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Data')
st.download_button(label="🖨️ พิมพ์รายงาน (ดาวน์โหลด Excel)", data=buffer.getvalue(), file_name="report.xlsx", mime="application/vnd.ms-excel")

# กราฟ
fig = px.bar(summary, x='บัญชี', y='ยอดคงเหลือ', color='บัญชี', title="กราฟเปรียบเทียบแต่ละบัญชี")
st.plotly_chart(fig, use_container_width=True)