import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import io

# --- ตั้งค่าหน้าจอและ CSS ธีมหวานแหวว สีชมพูพาสเทลสุดโรแมนติก ---
st.set_page_config(page_title="สมุดบัญชี รายรับ รายจ่าย 2026", layout="wide")

st.markdown("""
    <style>
    /* Background สีชมพู-พีชพาสเทล หวานละมุน */
    .stApp {
        background: linear-gradient(135deg, #fdf2f8 0%, #fff1f2 50%, #fef3c7 100%);
    }
    
    html, body, [class*="css"] {
        font-size: 18px !important;
    }

    h1 {
        font-size: 2.8rem !important;
        color: #db2777 !important;
        text-shadow: 2px 2px 4px rgba(219, 39, 119, 0.15);
    }
    h2, h3 {
        font-size: 1.8rem !important;
        color: #be185d !important;
    }

    /* แต่ง Sidebar ธีมหวานแหวว */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #fff1f2 100%);
        box-shadow: 6px 0 20px rgba(244, 63, 94, 0.15);
        min-width: 360px !important;
        border-right: 2px solid #fbcfe8;
    }

    section[data-testid="stSidebar"] h2 {
        color: #e11d48 !important;
        font-weight: 800 !important;
        border-bottom: 3px solid #f43f5e;
        padding-bottom: 8px;
    }

    section[data-testid="stSidebar"] label {
        font-size: 19px !important;
        font-weight: bold !important;
        color: #881337 !important;
    }

    /* ช่องกรอกข้อมูลให้มีกรอบสี่เหลี่ยมล้อมรอบชัดเจน */
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    div[data-testid="stSidebar"] div[data-baseweb="base-input"] {
        background-color: #fff1f2 !important;
        border: 2.5px solid #f43f5e !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        color: #9f1239 !important;
        font-size: 18px !important;
    }

    section[data-testid="stSidebar"] input:focus, 
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
        border-color: #f59e0b !important;
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.6) !important;
        background-color: #fffbeb !important;
    }

    /* ปุ่มบันทึกข้อมูล */
    div.stButton > button {
        color: white !important;
        border: none;
        padding: 18px 28px;
        text-align: center;
        font-size: 20px !important;
        font-weight: 900 !important;
        cursor: pointer;
        border-radius: 14px;
        background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
        box-shadow: 0 6px #be185d, 0 10px 20px rgba(244, 63, 94, 0.4);
        transition: all 0.15s ease-in-out;
        width: 100%;
        letter-spacing: 1px;
    }
    
    div.stButton > button:active {
        box-shadow: 0 2px #be185d;
        transform: translateY(4px);
    }
    
    div[data-testid="stVerticalBlock"] > div > div > div > div[data-testid="stHorizontalBlock"] > div:first-child > div > div > button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        box-shadow: 0 5px #b45309 !important;
        width: auto;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }

    div.stDownloadButton > button {
        background: linear-gradient(135deg, #ec4899 0%, #be185d 100%) !important;
        box-shadow: 0 5px #9d174d !important;
        width: auto;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        font-size: 18px !important;
        padding: 14px 24px;
    }

    div[data-testid="stDataEditor"] {
        border-radius: 12px;
        box-shadow: 0 6px 16px rgba(244, 63, 94, 0.12);
        border: 2px solid #fbcfe8;
    }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "data.csv"
columns_order = ["บัญชี", "รายการ", "วันที่", "รายรับ", "รายจ่าย"]
valid_accounts = ["ธกส (เจ้านาย)", "กสิกรไทย (เจ้านาย)", "กสิกรไทย (น้องจอย)", "เงินสด"]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=columns_order).to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

def get_data():
    df = pd.read_csv(DATA_FILE)
    for col in columns_order:
        if col not in df.columns:
            df[col] = 0 if col in ["รายรับ", "รายจ่าย"] else ""
    return df[columns_order]

st.title("📖 สมุดบัญชี รายรับ รายจ่าย 2026 💖")

# 1. ฟอร์มบันทึกข้อมูลทาง Sidebar
with st.sidebar.form("input_form", clear_on_submit=True):
    st.header("✨ บันทึกรายการ ✨")
    account = st.selectbox("📂 บัญชี", valid_accounts)
    item = st.text_input("📝 รายการ")
    amount_type = st.radio("⚡ ประเภท (รายรับ/รายจ่าย)", ["รายรับ", "รายจ่าย"])
    amount = st.number_input("💰 จำนวนเงิน (บาท)", min_value=0.0, step=1.0)
    date_input = st.date_input("📅 วันที่", datetime.now())
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.form_submit_button("🚀 บันทึกข้อมูลทันที"): 
        new_row = {
            "บัญชี": account,
            "รายการ": item,
            "วันที่": str(date_input),
            "รายรับ": amount if amount_type == "รายรับ" else 0, 
            "รายจ่าย": amount if amount_type == "รายจ่าย" else 0
        }
        new_df = pd.DataFrame([new_row])[columns_order]
        new_df.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
        st.rerun()

# โหลดข้อมูลทั้งหมด
df = get_data()
df['รายรับ'] = pd.to_numeric(df['รายรับ'], errors='coerce').fillna(0)
df['รายจ่าย'] = pd.to_numeric(df['รายจ่าย'], errors='coerce').fillna(0)

# KPI Cards ด้านบนสุด
st.subheader("📊 ภาพรวมยอดเงินทั้งหมด")
total_income = df['รายรับ'].sum()
total_expense = df['รายจ่าย'].sum()
total_balance = total_income - total_expense

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="💵 รายรับรวมทั้งหมด", value=f"{total_income:,.2f} ฿")
kpi2.metric(label="💸 รายจ่ายรวมทั้งหมด", value=f"{total_expense:,.2f} ฿")
kpi3.metric(label="💎 ยอดสุทธิคงเหลือรวม", value=f"{total_balance:,.2f} ฿")

st.divider()

# ตัวกรองค้นหาข้อมูล
st.subheader("🔍 ตัวกรองค้นหาข้อมูล")
filter_col1, _ = st.columns([2, 2])
all_accounts = ["ทั้งหมด"] + valid_accounts
selected_filter_account = filter_col1.selectbox("กรองดูเฉพาะบัญชี", all_accounts)

filtered_df = df if selected_filter_account == "ทั้งหมด" else df[df['บัญชี'] == selected_filter_account]

# ตารางรายการ
st.subheader("📋 รายการทั้งหมด (แก้ไขได้โดยตรง)")
edited_df = st.data_editor(filtered_df, num_rows="dynamic", use_container_width=True)

if st.button("🔄 อัปเดตและบันทึกข้อมูลใหม่"): 
    for col in ["รายรับ", "รายจ่าย"]:
        edited_df[col] = pd.to_numeric(edited_df[col], errors='coerce').fillna(0)
    
    if selected_filter_account != "ทั้งหมด":
        other_df = df[df['บัญชี'] != selected_filter_account]
        final_save_df = pd.concat([other_df, edited_df], ignore_index=True)
    else:
        final_save_df = edited_df
        
    final_save_df[columns_order].to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
    st.success("อัปเดตข้อมูลเรียบร้อย!")
    st.rerun()

# สรุปยอดคงเหลือแต่ละบัญชี (Fix ให้แสดงชื่อบัญชีจริงและยอดตรงเป๊ะ)
st.subheader("💎 สรุปยอดคงเหลือแยกตามบัญชี")

# สร้างตารางสรุปครบทุกบัญชีหลัก (แม้บัญชีไหนยังไม่มีรายการ ก็จะแสดงยอด 0.00 บาทให้เห็นชัดเจน)
summary_list = []
for acc in valid_accounts:
    acc_df = df[df['บัญชี'] == acc]
    acc_income = acc_df['รายรับ'].sum()
    acc_expense = acc_df['รายจ่าย'].sum()
    acc_balance = acc_income - acc_expense
    summary_list.append({"บัญชี": acc, "ยอดคงเหลือ": acc_balance})

summary_df = pd.DataFrame(summary_list)

if not summary_df.empty:
    cols = st.columns(len(valid_accounts))
    for i, row in summary_df.iterrows():
        cols[i].metric(label=row['บัญชี'], value=f"{row['ยอดคงเหลือ']:,.2f} ฿")

# ปุ่มพิมพ์ / ดาวน์โหลดรายงาน Excel
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Data')
st.download_button(label="🖨️ พิมพ์รายงาน (ดาวน์โหลด Excel)", data=buffer.getvalue(), file_name="report_2026.xlsx", mime="application/vnd.ms-excel")

# กราฟแสดงผลเปรียบเทียบ
if not summary_df.empty:
    st.divider()
    fig = px.bar(summary_df, x='บัญชี', y='ยอดคงเหลือ', color='บัญชี', title="📊 กราฟเปรียบเทียบยอดคงเหลือแต่ละบัญชี")
    st.plotly_chart(fig, use_container_width=True)