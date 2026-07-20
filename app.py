import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO  # <--- เพิ่มบรรทัดนี้เข้าไปครับ!

# ตั้งค่าหน้าเพจ
st.set_page_config(page_title="Financial Intelligence 2026", layout="wide")
st.title("📊 Financial Intelligence 2026")
DB_FILE = "finance_data.xlsx"

# 1. ฟังก์ชันโหลดข้อมูลแบบปลอดภัย
def load_data():
    cols = ["วันที่บันทึก", "เดือน/ปี", "บัญชี", "รายการ", "ยอดยกมา", "รายรับ", "รายจ่าย", "ยอดคงเหลือ"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_excel(DB_FILE)
            # ถ้าคอลัมน์ไม่ครบให้เติมค่าว่าง
            for col in cols:
                if col not in df.columns:
                    df[col] = 0 if col != "รายการ" and col != "บัญชี" and col != "วันที่บันทึก" and col != "เดือน/ปี" else ""
            return df
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# 2. Initialize State
if "df" not in st.session_state:
    st.session_state.df = load_data()

if "accounts" not in st.session_state:
    st.session_state.accounts = ["ธ.ก.ส.", "กสิกร(เจ้านาย)", "กสิกร(แฟน)"]

# 3. จัดการบัญชีใน Sidebar
st.sidebar.header("🏦 จัดการบัญชี")
new_acc = st.sidebar.text_input("เพิ่มบัญชีใหม่:")
if st.sidebar.button("เพิ่มบัญชี"):
    if new_acc and new_acc not in st.session_state.accounts:
        st.session_state.accounts.append(new_acc)
        st.rerun()

# 4. ฟังก์ชันคำนวณยอดคงเหลือ Realtime
def update_balances(df):
    if df.empty: return df
    for acc in st.session_state.accounts:
        acc_df = df[df['บัญชี'] == acc].copy()
        if not acc_df.empty:
            bal = 0
            for idx, row in acc_df.iterrows():
                bal = bal + float(row['ยอดยกมา']) + float(row['รายรับ']) - float(row['รายจ่าย'])
                df.at[idx, 'ยอดคงเหลือ'] = bal
    return df

# 5. Dashboard สรุปยอด
st.subheader("💰 สรุปยอดคงเหลือรายบัญชี")
cols = st.columns(len(st.session_state.accounts))
for i, acc in enumerate(st.session_state.accounts):
    acc_data = st.session_state.df[st.session_state.df['บัญชี'] == acc]
    acc_bal = acc_data['ยอดคงเหลือ'].iloc[-1] if not acc_data.empty else 0
    cols[i].metric(acc, f"{acc_bal:,.2f}")

st.divider()

# 6. ฟอร์มบันทึก
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

# 7. ตารางจัดการข้อมูล
st.subheader("📝 รายการทั้งหมด")
edited_df = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
if st.button("💾 บันทึกการแก้ไข (Update Balance)"):
    st.session_state.df = update_balances(edited_df)
    st.session_state.df.to_excel(DB_FILE, index=False)
    st.rerun()

# 8. ปุ่มดาวน์โหลดข้อมูลเป็น Excel
st.divider()
st.subheader("📥 ส่งออกข้อมูล (Export to Excel)")

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

df_xlsx = to_excel(st.session_state.df)
st.download_button(
    label="💾 ดาวน์โหลดข้อมูลทั้งหมด (.xlsx)",
    data=df_xlsx,
    file_name="Financial_Report_2026.xlsx",
    mime="application/vnd.ms-excel"
)