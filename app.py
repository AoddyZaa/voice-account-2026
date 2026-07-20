import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
import plotly.express as px

st.set_page_config(page_title="Financial Intelligence 2026", layout="wide")
st.title("📊 Financial Intelligence 2026")
DB_FILE = "finance_data.xlsx"

# ฟังก์ชันคำนวณที่แก้ Error ให้แล้ว
def calculate_balance(df):
    if df.empty: return df
    for acc in st.session_state.accounts:
        mask = df['บัญชี'] == acc
        # ใช้ .fillna(0) ป้องกันช่องว่าง และคำนวณสะสมให้เป็นค่าตัวเลขปกติ
        df.loc[mask, 'ยอดคงเหลือ'] = (pd.to_numeric(df.loc[mask, 'ยอดยกมา'], errors='coerce').fillna(0) + 
                                     pd.to_numeric(df.loc[mask, 'รายรับ'], errors='coerce').fillna(0) - 
                                     pd.to_numeric(df.loc[mask, 'รายจ่าย'], errors='coerce').fillna(0)).cumsum()
    return df

# โหลดข้อมูล
def load_data():
    cols = ["วันที่บันทึก", "เดือน/ปี", "บัญชี", "รายการ", "ยอดยกมา", "รายรับ", "รายจ่าย", "ยอดคงเหลือ"]
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE).fillna(0)
    return pd.DataFrame(columns=cols)

if "df" not in st.session_state: st.session_state.df = load_data()
if "accounts" not in st.session_state: st.session_state.accounts = ["ธ.ก.ส.", "กสิกร(เจ้านาย)", "กสิกร(แฟน)"]

# Sidebar
st.sidebar.header("🏦 จัดการบัญชี")
new_acc = st.sidebar.text_input("เพิ่มบัญชี:")
if st.sidebar.button("เพิ่มบัญชี") and new_acc and new_acc not in st.session_state.accounts:
    st.session_state.accounts.append(new_acc)
    st.rerun()

st.sidebar.divider()
st.sidebar.header("🔍 ตัวกรอง")
filter_acc = st.sidebar.multiselect("เลือกบัญชี:", st.session_state.accounts, default=st.session_state.accounts)
display_df = st.session_state.df[st.session_state.df['บัญชี'].isin(filter_acc)]

# สรุปยอด
st.subheader("💰 สรุปยอดคงเหลือ")
cols = st.columns(len(st.session_state.accounts))
for i, acc in enumerate(st.session_state.accounts):
    acc_data = st.session_state.df[st.session_state.df['บัญชี'] == acc]
    bal = acc_data['ยอดคงเหลือ'].iloc[-1] if not acc_data.empty else 0
    cols[i].metric(acc, f"{float(bal):,.2f}")

# ฟอร์มบันทึก
with st.form("entry_form", clear_on_submit=True): # <--- ใส่ clear_on_submit=True ตรงนี้ครับ
    c1, c2, c3, c4 = st.columns(4)
    acc = c1.selectbox("บัญชี:", st.session_state.accounts, key="acc_in")
    typ = c2.selectbox("ประเภท:", ["ยอดยกมา", "รายรับ", "รายจ่าย"], key="typ_in")
    item = c3.text_input("รายการ:", key="item_in")
    amt = c4.number_input("จำนวนเงิน:", min_value=0.0, key="amt_in")
    
    if st.form_submit_button("🚀 บันทึกรายการ"):
        new_data = {
            "วันที่บันทึก": datetime.now().strftime("%d/%m/%Y"), 
            "เดือน/ปี": datetime.now().strftime("%m/%Y"),
            "บัญชี": acc, "รายการ": item,
            "รายรับ": amt if typ=="รายรับ" else 0, 
            "รายจ่าย": amt if typ=="รายจ่าย" else 0, 
            "ยอดยกมา": amt if typ=="ยอดยกมา" else 0, 
            "ยอดคงเหลือ": 0
        }
        st.session_state.df = calculate_balance(pd.concat([st.session_state.df, pd.DataFrame([new_data])], ignore_index=True))
        st.session_state.df.to_excel(DB_FILE, index=False)
        st.rerun() # พอสั่ง rerun หน้าจอจะรีเฟรช และ clear_on_submit จะเคลียร์ช่องให้เองครับ

# ตารางและกราฟ
st.subheader("📈 กราฟและรายการ")
if not display_df.empty:
    fig = px.bar(display_df, x="วันที่บันทึก", y=["รายรับ", "รายจ่าย"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

edited_df = st.data_editor(display_df, num_rows="dynamic", use_container_width=True)
if st.button("💾 บันทึกการแก้ไข"):
    st.session_state.df = calculate_balance(edited_df)
    st.session_state.df.to_excel(DB_FILE, index=False)
    st.rerun()

# ดาวน์โหลด
def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.download_button("💾 ดาวน์โหลดไฟล์ Excel", data=to_excel_bytes(st.session_state.df), file_name="Financial_Report.xlsx")

