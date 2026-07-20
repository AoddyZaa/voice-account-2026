import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from io import BytesIO

st.set_page_config(page_title="Financial Intelligence 2026", layout="wide")
st.title("📊 Financial Intelligence 2026")
DB_FILE = "finance_data.xlsx"

# โหลดหรือสร้างข้อมูล
def load_data():
    cols = ["วันที่บันทึก", "เดือน/ปี", "บัญชี", "รายการ", "ยอดยกมา", "รายรับ", "รายจ่าย", "ยอดคงเหลือ"]
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    return pd.DataFrame(columns=cols)

if "df" not in st.session_state:
    st.session_state.df = load_data()

# จัดการบัญชีใน Sidebar
st.sidebar.header("🏦 จัดการบัญชี")
if "accounts" not in st.session_state:
    st.session_state.accounts = ["ธ.ก.ส.", "กสิกร(เจ้านาย)", "กสิกร(แฟน)"]

new_acc = st.sidebar.text_input("เพิ่มบัญชีใหม่:")
if st.sidebar.button("เพิ่มบัญชี"):
    if new_acc and new_acc not in st.session_state.accounts:
        st.session_state.accounts.append(new_acc)
        st.rerun()

# ฟังก์ชันคำนวณยอดคงเหลือแยกบัญชีแบบ Realtime
def update_balances(df):
    if df.empty: return df
    # คำนวณยอดคงเหลือแยกรายบัญชี
    for acc in st.session_state.accounts:
        acc_df = df[df['บัญชี'] == acc].copy()
        if not acc_df.empty:
            bal = 0
            for idx, row in acc_df.iterrows():
                bal = bal + float(row['ยอดยกมา']) + float(row['รายรับ']) - float(row['รายจ่าย'])
                df.at[idx, 'ยอดคงเหลือ'] = bal
    return df

# ส่วนสรุปยอด Realtime (Dashboard)
st.subheader("💰 สรุปยอดคงเหลือรายบัญชี")
cols = st.columns(len(st.session_state.accounts))
for i, acc in enumerate(st.session_state.accounts):
    acc_bal = st.session_state.df[st.session_state.df['บัญชี'] == acc]['ยอดคงเหลือ'].iloc[-1] if not st.session_state.df[st.session_state.df['บัญชี'] == acc].empty else 0
    cols[i].metric(acc, f"{acc_bal:,.2f}")

st.divider()

# ฟอร์มบันทึกรายการ
st.subheader("➕ บันทึกรายการใหม่")
with st.form("entry_form", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    chosen_account = c1.selectbox("เลือกบัญชี:", st.session_state.accounts)
    chosen_type = c2.selectbox("ประเภท:", ["ยอดยกมา", "รายรับ", "รายจ่าย"])
    item_name = c3.text_input("📝 รายการ:")
    amount = c4.number_input("💵 จำนวนเงิน:", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("🚀 บันทึกรายการ")

    if submitted:
        now = datetime.now()
        new_row = pd.DataFrame([{
            "วันที่บันทึก": now.strftime("%d/%m/%Y"), "เดือน/ปี": f"{now.month}/{now.year}",
            "บัญชี": chosen_account, "รายการ": item_name,
            "ยอดยกมา": amount if chosen_type=="ยอดยกมา" else 0,
            "รายรับ": amount if chosen_type=="รายรับ" else 0,
            "รายจ่าย": amount if chosen_type=="รายจ่าย" else 0, "ยอดคงเหลือ": 0
        }])
        st.session_state.df = update_balances(pd.concat([st.session_state.df, new_row], ignore_index=True))
        st.session_state.df.to_excel(DB_FILE, index=False)
        st.rerun()

# จัดการรายการ
st.subheader("📝 รายการทั้งหมด")
edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
if st.button("💾 บันทึกการแก้ไข (Update Balance)"):
    st.session_state.df = update_balances(edited_df)
    st.session_state.df.to_excel(DB_FILE, index=False)
    st.rerun()