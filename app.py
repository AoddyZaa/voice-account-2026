import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from io import BytesIO

st.set_page_config(page_title="Financial Intel 2026", layout="wide")
st.title("📊 Financial Intelligence 2026")
DB_FILE = "finance_data.xlsx"

TH_MONTHS = {"01": "มกราคม", "02": "กุมภาพันธ์", "03": "มีนาคม", "04": "เมษายน", "05": "พฤษภาคม", "06": "มิถุนายน", "07": "กรกฎาคม", "08": "สิงหาคม", "09": "กันยายน", "10": "ตุลาคม", "11": "พฤศจิกายน", "12": "ธันวาคม"}

def calculate_balance(df):
    if df.empty: return df
    bal = 0
    new_balances = []
    for _, row in df.iterrows():
        bal = bal + float(row['ยอดยกมา']) + float(row['รายรับ']) - float(row['รายจ่าย'])
        new_balances.append(bal)
    df['ยอดคงเหลือ'] = new_balances
    return df

def load_data():
    expected_cols = ["วันที่บันทึก", "เดือน/ปี", "รายการ", "ยอดยกมา", "รายรับ", "รายจ่าย", "ยอดคงเหลือ"]
    if os.path.exists(DB_FILE):
        df = pd.read_excel(DB_FILE)
        if not all(col in df.columns for col in expected_cols):
            return pd.DataFrame(columns=expected_cols)
        return df
    return pd.DataFrame(columns=expected_cols)

if "df" not in st.session_state or not all(col in st.session_state.df.columns for col in ["วันที่บันทึก", "เดือน/ปี", "รายการ", "ยอดยกมา", "รายรับ", "รายจ่าย", "ยอดคงเหลือ"]):
    st.session_state.df = load_data()

# Sidebar: กรองข้อมูล + ค้นหารายการ
st.sidebar.header("🔍 กรองและค้นหา")
months = sorted(list(set(st.session_state.df['เดือน/ปี'].dropna()))) if not st.session_state.df.empty else []
selected_month = st.sidebar.selectbox("เลือกเดือน:", ["ทั้งหมด"] + months)
search_query = st.sidebar.text_input("🔍 ค้นหารายการ:")

filtered_df = st.session_state.df
if selected_month != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df['เดือน/ปี'] == selected_month]
if search_query:
    filtered_df = filtered_df[filtered_df['รายการ'].str.contains(search_query, na=False)]

# Dashboard
col1, col2, col3 = st.columns(3)
col1.metric("รายรับรวม", f"{filtered_df['รายรับ'].sum():,.2f}")
col2.metric("รายจ่ายรวม", f"{filtered_df['รายจ่าย'].sum():,.2f}")
col3.metric("ยอดคงเหลือปัจจุบัน", f"{st.session_state.df['ยอดคงเหลือ'].iloc[-1] if not st.session_state.df.empty else 0:,.2f}")

# เพิ่มกราฟสรุป
if not filtered_df.empty:
    chart_data = filtered_df[['เดือน/ปี', 'รายรับ', 'รายจ่าย']].melt(id_vars='เดือน/ปี', var_name='ประเภท', value_name='จำนวนเงิน')
    fig = px.bar(chart_data, x='เดือน/ปี', y='จำนวนเงิน', color='ประเภท', barmode='group', title="กราฟสรุปรายรับ-รายจ่าย")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ฟอร์มบันทึก
with st.expander("➕ บันทึกรายการใหม่"):
    c1, c2, c3 = st.columns(3)
    chosen_type = c1.selectbox("ประเภท:", ["ยอดยกมา", "รายรับ", "รายจ่าย"])
    item_name = c2.text_input("📝 รายการ:")
    amount = c3.number_input("💵 จำนวนเงิน:", min_value=0.0, format="%.2f")
    if st.button("🚀 บันทึก"):
        now = datetime.now()
        month_year_str = f"{TH_MONTHS[now.strftime('%m')]} {now.year + 543}"
        new_row = pd.DataFrame([{"วันที่บันทึก": now.strftime("%d/%m/%Y"), "เดือน/ปี": month_year_str, "รายการ": item_name, "ยอดยกมา": amount if chosen_type=="ยอดยกมา" else 0, "รายรับ": amount if chosen_type=="รายรับ" else 0, "รายจ่าย": amount if chosen_type=="รายจ่าย" else 0, "ยอดคงเหลือ": 0}])
        st.session_state.df = calculate_balance(pd.concat([st.session_state.df, new_row], ignore_index=True))
        st.session_state.df.to_excel(DB_FILE, index=False)
        st.rerun()

st.subheader("📝 จัดการรายการ")
edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
c_btn1, c_btn2 = st.columns([1, 4])
if c_btn1.button("🗑️ ยืนยันการลบ / อัปเดต"):
    st.session_state.df = calculate_balance(edited_df)
    st.session_state.df.to_excel(DB_FILE, index=False)
    st.rerun()

output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, index=False)
c_btn2.download_button("🖨️ พิมพ์ข้อมูลออกเป็น Excel", output.getvalue(), f"Financial_Report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")