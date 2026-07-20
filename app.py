import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO

st.set_page_config(page_title="Financial Intel 2026", layout="wide")

st.markdown("<style>.stApp {background-color: #f8f9fa;}</style>", unsafe_allow_html=True)

st.title("📊 Financial Intelligence 2026")
DB_FILE = "finance_data.xlsx"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    return pd.DataFrame(columns=["วันที่/เดือน", "รายการ", "ยอดยกมา", "รายรับ", "รายจ่าย", "ยอดคงเหลือ"])

if "df" not in st.session_state:
    st.session_state.df = load_data()

# --- ระบบตัวกรองเดือน (Sidebar) ---
st.sidebar.header("🔍 กรองข้อมูล")
if not st.session_state.df.empty:
    # ดึงเฉพาะเดือนจากคอลัมน์ วันที่/เดือน (เช่น '07')
    months = sorted(list(set([x.split('/')[1] for x in st.session_state.df['วันที่/เดือน'] if isinstance(x, str)])))
    selected_month = st.sidebar.selectbox("เลือกเดือนที่ต้องการดู:", ["ทั้งหมด"] + months)
else:
    selected_month = "ทั้งหมด"

# กรองข้อมูลตามที่เลือก
filtered_df = st.session_state.df
if selected_month != "ทั้งหมด":
    filtered_df = st.session_state.df[st.session_state.df['วันที่/เดือน'].apply(lambda x: x.split('/')[1] == selected_month)]

# Dashboard สรุปยอด (สรุปจากที่กรองแล้ว)
col1, col2, col3 = st.columns(3)
col1.metric("รายรับรวม", f"{filtered_df['รายรับ'].sum():,.2f}")
col2.metric("รายจ่ายรวม", f"{filtered_df['รายจ่าย'].sum():,.2f}")
col3.metric("ยอดคงเหลือ (ที่กรอง)", f"{filtered_df['ยอดคงเหลือ'].iloc[-1] if not filtered_df.empty else 0:,.2f}")

st.divider()

# ฟอร์มบันทึก
with st.expander("➕ บันทึกรายการใหม่", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        chosen_type = st.selectbox("ประเภท:", ["ยอดยกมา", "รายรับ", "รายจ่าย"])
    with c2:
        item_name = st.text_input("📝 รายการ:")
    with c3:
        amount = st.number_input("💵 จำนวนเงิน:", min_value=0.0, format="%.2f")
    
    if st.button("🚀 บันทึกเข้าสู่ระบบ"):
        prev_bal = st.session_state.df["ยอดคงเหลือ"].iloc[-1] if not st.session_state.df.empty else 0.0
        row = {
            "วันที่/เดือน": datetime.now().strftime("%d/%m"), "รายการ": item_name, 
            "ยอดยกมา": amount if chosen_type=="ยอดยกมา" else 0,
            "รายรับ": amount if chosen_type=="รายรับ" else 0,
            "รายจ่าย": amount if chosen_type=="รายจ่าย" else 0,
            "ยอดคงเหลือ": prev_bal + (amount if chosen_type != "รายจ่าย" else -amount)
        }
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([row])], ignore_index=True)
        st.session_state.df.to_excel(DB_FILE, index=False)
        st.rerun()

# ตารางแสดงผลที่ผ่านการกรองแล้ว
st.dataframe(filtered_df, use_container_width=True)

# ดาวน์โหลด
buffer = BytesIO()
st.session_state.df.to_excel(buffer, index=False)
st.download_button("📥 Export ข้อมูลทั้งหมดเป็น Excel", buffer, "Finance_Report_2026.xlsx", "application/vnd.ms-excel")