import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO

st.set_page_config(page_title="Financial Intel 2026", layout="wide")

st.markdown("<style>.stApp {background-color: #f8f9fa;}</style>", unsafe_allow_html=True)

st.title("📊 Financial Intelligence 2026")
DB_FILE = "finance_data.xlsx"

# ตารางชื่อเดือนภาษาไทย
TH_MONTHS = {
    "01": "มกราคม", "02": "กุมภาพันธ์", "03": "มีนาคม", "04": "เมษายน",
    "05": "พฤษภาคม", "06": "มิถุนายน", "07": "กรกฎาคม", "08": "สิงหาคม",
    "09": "กันยายน", "10": "ตุลาคม", "11": "พฤศจิกายน", "12": "ธันวาคม"
}

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    return pd.DataFrame(columns=["วันที่บันทึก", "เดือน/ปี", "รายการ", "ยอดยกมา", "รายรับ", "รายจ่าย", "ยอดคงเหลือ"])

if "df" not in st.session_state:
    st.session_state.df = load_data()

def reset_form():
    st.session_state.item_name = ""
    st.session_state.amount = 0.0

if 'item_name' not in st.session_state: st.session_state.item_name = ""
if 'amount' not in st.session_state: st.session_state.amount = 0.0

# --- ระบบตัวกรอง (Sidebar) ---
st.sidebar.header("🔍 กรองข้อมูล")
if not st.session_state.df.empty:
    month_list = sorted(list(set(st.session_state.df['เดือน/ปี'])))
    selected_month = st.sidebar.selectbox("เลือกเดือนที่ต้องการดู:", ["ทั้งหมด"] + month_list)
else:
    selected_month = "ทั้งหมด"

filtered_df = st.session_state.df
if selected_month != "ทั้งหมด":
    filtered_df = st.session_state.df[st.session_state.df['เดือน/ปี'] == selected_month]

# Dashboard
col1, col2, col3 = st.columns(3)
col1.metric("รายรับรวม", f"{filtered_df['รายรับ'].sum():,.2f}")
col2.metric("รายจ่ายรวม", f"{filtered_df['รายจ่าย'].sum():,.2f}")
col3.metric("ยอดคงเหลือ", f"{filtered_df['ยอดคงเหลือ'].iloc[-1] if not filtered_df.empty else 0:,.2f}")

st.divider()

# ฟอร์มบันทึก
with st.expander("➕ บันทึกรายการใหม่", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        chosen_type = st.selectbox("ประเภท:", ["ยอดยกมา", "รายรับ", "รายจ่าย"], key="chosen_type")
    with c2:
        item_name = st.text_input("📝 รายการ:", key="item_name")
    with c3:
        amount = st.number_input("💵 จำนวนเงิน:", min_value=0.0, format="%.2f", key="amount")
    
    if st.button("🚀 บันทึกเข้าสู่ระบบ"):
        now = datetime.now()
        month_key = now.strftime("%m")
        # แปลงเป็น: กรกฎาคม 2569 (บวก ค.ศ. 543)
        month_year_str = f"{TH_MONTHS[month_key]} {now.year + 543}"
        
        prev_bal = st.session_state.df["ยอดคงเหลือ"].iloc[-1] if not st.session_state.df.empty else 0.0
        row = {
            "วันที่บันทึก": now.strftime("%d/%m/%Y"),
            "เดือน/ปี": month_year_str,
            "รายการ": item_name, 
            "ยอดยกมา": amount if chosen_type=="ยอดยกมา" else 0,
            "รายรับ": amount if chosen_type=="รายรับ" else 0,
            "รายจ่าย": amount if chosen_type=="รายจ่าย" else 0,
            "ยอดคงเหลือ": prev_bal + (amount if chosen_type != "รายจ่าย" else -amount)
        }
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([row])], ignore_index=True)
        st.session_state.df.to_excel(DB_FILE, index=False)
        reset_form()
        st.rerun()

st.dataframe(filtered_df, use_container_width=True)