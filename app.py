import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
import plotly.express as px # อย่าลืม pip install plotly ด้วยนะครับ

st.set_page_config(page_title="Financial Intelligence 2026", layout="wide")
st.title("📊 Financial Intelligence 2026")
DB_FILE = "finance_data.xlsx"

# 1. โหลดข้อมูล
def load_data():
    cols = ["วันที่บันทึก", "เดือน/ปี", "บัญชี", "รายการ", "ยอดยกมา", "รายรับ", "รายจ่าย", "ยอดคงเหลือ"]
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    return pd.DataFrame(columns=cols)

if "df" not in st.session_state: st.session_state.df = load_data()
if "accounts" not in st.session_state: st.session_state.accounts = ["ธ.ก.ส.", "กสิกร(เจ้านาย)", "กสิกร(แฟน)"]

# 2. Sidebar: จัดการบัญชี + ตัวกรอง
st.sidebar.header("🏦 จัดการบัญชี")
new_acc = st.sidebar.text_input("เพิ่มบัญชีใหม่:")
if st.sidebar.button("เพิ่มบัญชี") and new_acc:
    if new_acc not in st.session_state.accounts: st.session_state.accounts.append(new_acc)

st.sidebar.divider()
st.sidebar.header("🔍 ตัวกรองข้อมูล")
filter_acc = st.sidebar.multiselect("เลือกบัญชีที่จะดู:", st.session_state.accounts, default=st.session_state.accounts)

# กรองข้อมูล
display_df = st.session_state.df[st.session_state.df['บัญชี'].isin(filter_acc)]

# 3. Dashboard สรุปยอด
st.subheader("💰 สรุปยอดคงเหลือรายบัญชี")
cols = st.columns(len(st.session_state.accounts))
for i, acc in enumerate(st.session_state.accounts):
    acc_data = st.session_state.df[st.session_state.df['บัญชี'] == acc]
    bal = acc_data['ยอดคงเหลือ'].iloc[-1] if not acc_data.empty else 0
    cols[i].metric(acc, f"{bal:,.2f}")

# 4. กราฟ
if not display_df.empty:
    st.subheader("📈 กราฟแสดงรายรับ-รายจ่าย")
    fig = px.bar(display_df, x="วันที่บันทึก", y=["รายรับ", "รายจ่าย"], barmode="group", color_discrete_sequence=["#00CC96", "#EF553B"])
    st.plotly_chart(fig, use_container_width=True)

# 5. ฟอร์มบันทึก
with st.form("entry_form"):
    c1, c2, c3, c4 = st.columns(4)
    chosen_account = c1.selectbox("บัญชี:", st.session_state.accounts)
    chosen_type = c2.selectbox("ประเภท:", ["ยอดยกมา", "รายรับ", "รายจ่าย"])
    item_name = c3.text_input("รายการ:")
    amount = c4.number_input("จำนวนเงิน:", min_value=0.0)
    if st.form_submit_button("🚀 บันทึกรายการ"):
        new_row = pd.DataFrame([{"วันที่บันทึก": datetime.now().strftime("%d/%m/%Y"), "บัญชี": chosen_account, "รายการ": item_name, "รายรับ": amount if chosen_type=="รายรับ" else 0, "รายจ่าย": amount if chosen_type=="รายจ่าย" else 0, "ยอดยกมา": amount if chosen_type=="ยอดยกมา" else 0}])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        st.session_state.df.to_excel(DB_FILE, index=False)
        st.rerun()

# 6. ตาราง
st.subheader("📝 รายการทั้งหมด")
edited_df = st.data_editor(display_df, use_container_width=True)
if st.button("💾 บันทึกการแก้ไข"):
    st.session_state.df = edited_df
    st.session_state.df.to_excel(DB_FILE, index=False)
    st.rerun()

# เพิ่มปุ่มดาวน์โหลดต่อท้ายตาราง
st.divider()
st.subheader("📥 ส่งออกข้อมูล (Export to Excel)")

# ฟังก์ชันแปลง DataFrame เป็น Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# สร้างปุ่มดาวน์โหลด
df_xlsx = to_excel(st.session_state.df)
st.download_button(
    label="💾 ดาวน์โหลดไฟล์ Excel",
    data=df_xlsx,
    file_name="Financial_Report_2026.xlsx",
    mime="application/vnd.ms-excel"
)