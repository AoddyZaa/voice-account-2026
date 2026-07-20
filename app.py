import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO

st.set_page_config(page_title="Financial Intel 2026", layout="wide")
st.title("📊 Financial Intelligence 2026")
DB_FILE = "finance_data.xlsx"

TH_MONTHS = {"01": "มกราคม", "02": "กุมภาพันธ์", "03": "มีนาคม", "04": "เมษายน", "05": "พฤษภาคม", "06": "มิถุนายน", "07": "กรกฎาคม", "08": "สิงหาคม", "09": "กันยายน", "10": "ตุลาคม", "11": "พฤศจิกายน", "12": "ธันวาคม"}

def load_data():
    expected_cols = ["วันที่บันทึก", "เดือน/ปี", "รายการ", "ยอดยกมา", "รายรับ", "รายจ่าย", "ยอดคงเหลือ"]
    if os.path.exists(DB_FILE):
        df = pd.read_excel(DB_FILE)
        # ถ้าโหลดมาแล้วคอลัมน์ไม่ครบ ให้สร้างใหม่ทันที
        if not all(col in df.columns for col in expected_cols):
            return pd.DataFrame(columns=expected_cols)
        return df
    return pd.DataFrame(columns=expected_cols)

# และเพิ่มบรรทัดนี้ไปใต้บรรทัดที่โหลด load_data() เพื่อเคลียร์ค่าเก่าที่ค้างอยู่:
if "df" not in st.session_state or not all(col in st.session_state.df.columns for col in ["วันที่บันทึก", "เดือน/ปี", "รายการ", "ยอดยกมา", "รายรับ", "รายจ่าย", "ยอดคงเหลือ"]):
    st.session_state.df = load_data()

# Sidebar: กรองข้อมูล
st.sidebar.header("🔍 กรองข้อมูล")
months = sorted(list(set(st.session_state.df['เดือน/ปี'].dropna()))) if not st.session_state.df.empty else []
selected_month = st.sidebar.selectbox("เลือกเดือนที่ต้องการดู:", ["ทั้งหมด"] + months)

# Dashboard
filtered_df = st.session_state.df
if selected_month != "ทั้งหมด":
    filtered_df = st.session_state.df[st.session_state.df['เดือน/ปี'] == selected_month]

col1, col2, col3 = st.columns(3)
col1.metric("รายรับรวม", f"{filtered_df['รายรับ'].sum():,.2f}")
col2.metric("รายจ่ายรวม", f"{filtered_df['รายจ่าย'].sum():,.2f}")
col3.metric("ยอดคงเหลือปัจจุบัน", f"{st.session_state.df['ยอดคงเหลือ'].iloc[-1] if not st.session_state.df.empty else 0:,.2f}")

st.divider()

# ฟอร์มบันทึก
if 'form_key' not in st.session_state: st.session_state.form_key = 0
with st.expander("➕ บันทึกรายการใหม่", expanded=True):
    c1, c2, c3 = st.columns(3)
    chosen_type = c1.selectbox("ประเภท:", ["ยอดยกมา", "รายรับ", "รายจ่าย"], key=f"type_{st.session_state.form_key}")
    item_name = c2.text_input("📝 รายการ:", key=f"item_{st.session_state.form_key}")
    amount = c3.number_input("💵 จำนวนเงิน:", min_value=0.0, format="%.2f", key=f"amt_{st.session_state.form_key}")
    
    if st.button("🚀 บันทึกเข้าสู่ระบบ"):
        now = datetime.now()
        month_year_str = f"{TH_MONTHS[now.strftime('%m')]} {now.year + 543}"
        new_row = pd.DataFrame([{
            "วันที่บันทึก": now.strftime("%d/%m/%Y"), "เดือน/ปี": month_year_str, "รายการ": item_name, 
            "ยอดยกมา": amount if chosen_type=="ยอดยกมา" else 0, "รายรับ": amount if chosen_type=="รายรับ" else 0, 
            "รายจ่าย": amount if chosen_type=="รายจ่าย" else 0, "ยอดคงเหลือ": 0
        }])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        st.session_state.df = calculate_balance(st.session_state.df)
        st.session_state.df.to_excel(DB_FILE, index=False)
        st.session_state.form_key += 1
        st.rerun()

# จัดการรายการ (ลบ/แก้ไข)
st.subheader("📝 จัดการรายการ")
edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")

# ปุ่มยืนยันและปุ่มพิมพ์
c_btn1, c_btn2 = st.columns([1, 4])
if c_btn1.button("🗑️ ยืนยันการลบ / อัปเดต"):
    st.session_state.df = calculate_balance(edited_df)
    st.session_state.df.to_excel(DB_FILE, index=False)
    st.rerun()

# ปุ่มพิมพ์รายงาน (Export Excel)
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, index=False)
c_btn2.download_button(
    label="🖨️ พิมพ์ข้อมูลออกเป็น Excel",
    data=output.getvalue(),
    file_name=f"Financial_Report_{selected_month}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)