import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
import plotly.express as px

st.set_page_config(page_title="Financial Intelligence 2026", layout="wide")
st.title("📊 Financial Intelligence 2026")
DB_FILE = "finance_data.xlsx"

# 1. โหลดข้อมูล
def load_data():
    cols = ["วันที่บันทึก", "เดือน/ปี", "บัญชี", "รายการ", "ยอดยกมา", "รายรับ", "รายจ่าย", "ยอดคงเหลือ"]
    if os.path.exists(DB_FILE):
        df = pd.read_excel(DB_FILE)
        return df.fillna(0)
    return pd.DataFrame(columns=cols)

if "df" not in st.session_state: st.session_state.df = load_data()
if "accounts" not in st.session_state: st.session_state.accounts = ["ธ.ก.ส.", "กสิกร(เจ้านาย)", "กสิกร(แฟน)"]

# 2. Sidebar: ตัวกรองและจัดการบัญชี
st.sidebar.header("🏦 จัดการบัญชี")
new_acc = st.sidebar.text_input("เพิ่มบัญชี:")
if st.sidebar.button("เพิ่มบัญชี") and new_acc and new_acc not in st.session_state.accounts:
    st.session_state.accounts.append(new_acc)
    st.rerun()

st.sidebar.divider()
st.sidebar.header("🔍 ตัวกรอง")
filter_acc = st.sidebar.multiselect("เลือกบัญชี:", st.session_state.accounts, default=st.session_state.accounts)
display_df = st.session_state.df[st.session_state.df['บัญชี'].isin(filter_acc)]

# 3. สรุปยอด
st.subheader("💰 สรุปยอดคงเหลือ")
cols = st.columns(len(st.session_state.accounts))
for i, acc in enumerate(st.session_state.accounts):
    acc_data = st.session_state.df[st.session_state.df['บัญชี'] == acc]
    bal = acc_data['ยอดคงเหลือ'].iloc[-1] if not acc_data.empty else 0
    cols[i].metric(acc, f"{float(bal):,.2f}")

# 4. ฟอร์มบันทึก
with st.form("entry_form"):
    c1, c2, c3, c4 = st.columns(4)
    acc = c1.selectbox("บัญชี:", st.session_state.accounts)
    typ = c2.selectbox("ประเภท:", ["ยอดยกมา", "รายรับ", "รายจ่าย"])
    item = c3.text_input("รายการ:")
    amt = c4.number_input("จำนวนเงิน:", min_value=0.0)
    if st.form_submit_button("🚀 บันทึกรายการ"):
        new_row = pd.DataFrame([{"วันที่บันทึก": datetime.now().strftime("%d/%m/%Y"), "บัญชี": acc, "รายการ": item, "รายรับ": amt if typ=="รายรับ" else 0, "รายจ่าย": amt if typ=="รายจ่าย" else 0, "ยอดยกมา": amt if typ=="ยอดยกมา" else 0, "ยอดคงเหลือ": 0}])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        st.session_state.df.to_excel(DB_FILE, index=False)
        st.rerun()

# 5. กราฟ
if not display_df.empty:
    st.subheader("📈 กราฟแสดงรายรับ-รายจ่าย")
    fig = px.bar(display_df, x="วันที่บันทึก", y=["รายรับ", "รายจ่าย"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# 6. ตาราง
st.subheader("📝 รายการทั้งหมด")
edited_df = st.data_editor(display_df, num_rows="dynamic", use_container_width=True)
if st.button("💾 บันทึกการแก้ไข (ลบแถวแล้วกดที่นี่)"):
    st.session_state.df = edited_df
    st.session_state.df.to_excel(DB_FILE, index=False)
    st.rerun()

# 7. ดาวน์โหลด (แก้ให้ถูกต้องครับ)
st.divider()
def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.download_button(
    label="💾 ดาวน์โหลดไฟล์ Excel",
    data=to_excel_bytes(st.session_state.df),
    file_name="Financial_Report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)