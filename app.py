import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import io
import requests

# --- ตั้งค่าหน้าจอและ CSS ธีมหวานแหวว ---
st.set_page_config(page_title="สมุดบัญชี รายรับ รายจ่าย 2026", layout="wide")

st.markdown("""
    <style>
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
        width: 100%;
        letter-spacing: 1px;
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

columns_order = ["บัญชี", "วันที่", "รายการ", "รายรับ", "รายจ่าย"]
valid_accounts = ["ธกส (ลุงอ๊อด)", "กสิกรไทย (ลุงอ๊อด)", "กสิกรไทย (น้องจอย)", "เงินสด"]

# ⚠️ ลิงก์ Web App ของเจ้านาย
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyNvSt-Ex1n5ix6rqn8Pn9QI1lqQQmlGke-hswGGyAUAPFDMomKXhaBmzWwvNaOJzBDhA/exec"

def format_thai_date(dt_obj):
    if pd.isna(dt_obj):
        return ""
    thai_months = [
        "", "กรากฎาคม" if False else "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", 
        "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", 
        "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    # แปลง ค.ศ. เป็น พ.ศ. (+543)
    try:
        if isinstance(dt_obj, str):
            dt_obj = pd.to_datetime(dt_obj)
        day = dt_obj.day
        month_idx = dt_obj.month
        year_th = dt_obj.year + 543
        thai_month_names = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        return f"{day} {thai_month_names[month_idx]} {year_th}"
    except:
        return str(dt_obj)

def get_data():
    try:
        response = requests.get(WEB_APP_URL)
        data = response.json()
        if not data or len(data) <= 1:
            return pd.DataFrame(columns=columns_order)
        
        header = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=header)
        for col in columns_order:
            if col not in df.columns:
                df[col] = 0 if col in ["รายรับ", "รายจ่าย"] else ""
        return df[columns_order]
    except Exception as e:
        return pd.DataFrame(columns=columns_order)

def save_data(df):
    try:
        payload = {
            "action": "save",
            "rows": [df.columns.values.tolist()] + df.values.tolist()
        }
        requests.post(WEB_APP_URL, json=payload)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึก: {e}")

st.title("📖 สมุดบัญชี รายรับ รายจ่าย 2026 💖")

with st.sidebar.form("input_form", clear_on_submit=True):
    st.header("✨ บันทึกรายการ ✨")
    account = st.selectbox("📂 บัญชี", valid_accounts)
    date_input = st.date_input("📅 วันที่", datetime.now())
    item = st.text_input("📝 รายการ")
    amount_type = st.radio("⚡ ประเภท (รายรับ/รายจ่าย)", ["รายรับ", "รายจ่าย"])
    amount = st.number_input("💰 จำนวนเงิน (บาท)", min_value=0.0, step=1.0)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.form_submit_button("🚀 บันทึกข้อมูลทันที"): 
        # แปลงวันที่ที่เลือกให้เป็นรูปแบบ วัน เดือน (ภาษาไทย) ปี พ.ศ. บันทึก
        formatted_date_str = format_thai_date(date_input)
        new_row = {
            "บัญชี": account,
            "วันที่": formatted_date_str,
            "รายการ": item,
            "รายรับ": amount if amount_type == "รายรับ" else 0, 
            "รายจ่าย": amount if amount_type == "รายจ่าย" else 0
        }
        df_current = get_data()
        new_df = pd.DataFrame([new_row])
        final_df = pd.concat([df_current, new_df], ignore_index=True)
        save_data(final_df)
        st.success("บันทึกข้อมูลลง Google Sheets เรียบร้อยครับ!")
        st.rerun()

df = get_data()
df['รายรับ'] = pd.to_numeric(df['รายรับ'], errors='coerce').fillna(0)
df['รายจ่าย'] = pd.to_numeric(df['รายจ่าย'], errors='coerce').fillna(0)

# สร้างคอลัมน์ช่วยเทียบเดือนจากข้อความวันที่ไทย หรือแปลงกลับเพื่อทำตัวกรอง
# (เพื่อให้ระบบกรองเดือนยังทำงานได้แม่นยำแม้ข้อมูลจะเป็นภาษาไทย)
thai_month_map = {
    "มกราคม": "01", "กุมภาพันธ์": "02", "มีนาคม": "03", "เมษายน": "04",
    "พฤษภาคม": "05", "มิถุนายน": "06", "กรกฎาคม": "07", "สิงหาคม": "08",
    "กันยายน": "09", "ตุลาคม": "10", "พฤศจิกายน": "11", "ธันวาคม": "12"
}

def extract_year_month(date_str):
    try:
        parts = str(date_str).split()
        if len(parts) >= 3:
            day = parts[0]
            m_name = parts[1]
            year_th = int(parts[2])
            year_ce = year_th - 543
            m_num = thai_month_map.get(m_name, "01")
            return f"{year_ce}-{m_num}"
    except:
        pass
    return "2026-07"

df['ปี-เดือน'] = df['วันที่'].apply(extract_year_month)

st.subheader("📊 ภาพรวมยอดเงินทั้งหมด")
total_income = df['รายรับ'].sum()
total_expense = df['รายจ่าย'].sum()
total_balance = total_income - total_expense

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="💵 รายรับรวมทั้งหมด", value=f"{total_income:,.2f} ฿")
kpi2.metric(label="💸 รายจ่ายรวมทั้งหมด", value=f"{total_expense:,.2f} ฿")
kpi3.metric(label="💎 ยอดสุทธิคงเหลือรวม", value=f"{total_balance:,.2f} ฿")

st.divider()

st.subheader("🔍 ตัวกรองค้นหาข้อมูล")
filter_col1, filter_col2 = st.columns(2)

all_accounts = ["ทั้งหมด"] + valid_accounts
selected_filter_account = filter_col1.selectbox("กรองดูเฉพาะบัญชี", all_accounts)

available_months = ["ทั้งหมด"] + sorted(df['ปี-เดือน'].dropna().unique().tolist(), reverse=True)
selected_month = filter_col2.selectbox("📅 กรองดูตามเดือน (ปี-เดือน)", available_months)

filtered_df = df.copy()
if selected_filter_account != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df['บัญชี'] == selected_filter_account]
if selected_month != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df['ปี-เดือน'] == selected_month]

display_df = filtered_df[columns_order]

st.subheader("📋 รายการทั้งหมด (แก้ไขได้โดยตรง)")
edited_df = st.data_editor(display_df, num_rows="dynamic", use_container_width=True, key="data_editor_view")

if st.button("🔄 อัปเดตและบันทึกข้อมูลใหม่"): 
    for col in ["รายรับ", "รายจ่าย"]:
        edited_df[col] = pd.to_numeric(edited_df[col], errors='coerce').fillna(0)
    
    if selected_filter_account != "ทั้งหมด" or selected_month != "ทั้งหมด":
        excluded_df = df[~df.index.isin(filtered_df.index)]
        final_save_df = pd.concat([excluded_df[columns_order], edited_df[columns_order]], ignore_index=True)
    else:
        final_save_df = edited_df[columns_order]
        
    save_data(final_save_df[columns_order])
    st.success("อัปเดตข้อมูลออนไลน์เรียบร้อย!")
    st.rerun()

st.subheader("💎 สรุปยอดคงเหลือแยกตามบัญชี")

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

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df[columns_order].to_excel(writer, index=False, sheet_name='Data')
st.download_button(label="🖨️ พิมพ์รายงาน (ดาวน์โหลด Excel)", data=buffer.getvalue(), file_name="report_2026.xlsx", mime="application/vnd.ms-excel")

if not summary_df.empty:
    st.divider()
    fig = px.bar(summary_df, x='บัญชี', y='ยอดคงเหลือ', color='บัญชี', title="📊 กราฟเปรียบเทียบยอดคงเหลือแต่ละบัญชี")
    st.plotly_chart(fig, use_container_width=True)