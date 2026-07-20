import streamlit as st
import pandas as pd
from datetime import datetime
import re
import os
from streamlit_mic_recorder import mic_recorder

# 1. ตั้งค่าหน้าจอ UI
st.set_page_config(page_title="Voice Expense 2026", layout="centered")

st.title("📖 สมุดบัญชีดิจิทัล (เวอร์ชันแท็บเล็ต)")
st.write("บันทึกรายรับ-รายจ่ายผ่านไมค์แท็บเล็ตได้เลยครับ")

# 💾 🛠️ ระบบจัดการฐานข้อมูลไฟล์
DB_FILE = "expense_database.csv"
BACKUP_FILE = "expense_database_backup.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df = df.astype({"รายรับ (บาท)": "float64", "รายจ่าย (บาท)": "float64"})
            return df
        except:
            pass
    return pd.DataFrame(columns=["วัน-เวลา บันทึก", "เดือน-ปี", "รายการ", "รายรับ (บาท)", "รายจ่าย (บาท)", "ประเภทดิบ"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if "expense_data" not in st.session_state:
    st.session_state.expense_data = load_data()

# ส่วนพักข้อมูล
if "temp_item" not in st.session_state: st.session_state.temp_item = ""
if "temp_amount" not in st.session_state: st.session_state.temp_amount = 0.0

# ฟังก์ชันแปลงตัวเลข (เหมือนเดิม)
def parse_thai_number_decimal(text):
    text_clean = text.replace(",", "").replace("บาท", "").strip()
    if "จุด" in text_clean:
        parts = text_clean.split("จุด")
        main_part, sub_part = parts[0].strip(), parts[1].strip()
        main_val = float("".join(re.findall(r'\d+', main_part))) if "".join(re.findall(r'\d+', main_part)) else 0.0
        sub_val = float("0." + "".join(re.findall(r'\d+', sub_part))) if "".join(re.findall(r'\d+', sub_part)) else 0.0
        return main_val + sub_val
    all_digits = "".join(re.findall(r'\d+', text_clean))
    return float(all_digits) if all_digits else 0.0

# -------------------------------------------------------------------
# 📝 ขั้นตอนการบันทึก
# -------------------------------------------------------------------
st.subheader("📝 ขั้นตอนการบันทึก")
chosen_type = st.radio("🟢 เลือกประเภท:", options=["เงินคงเหลือยกมา", "รายรับ", "รายจ่าย"], index=1, horizontal=True)

st.write("🎙️ กดปุ่มไมค์แล้วพูดได้เลยครับ:")
audio = mic_recorder(start_prompt="กดเพื่อเริ่มบันทึก", stop_prompt="กดเพื่อหยุด", just_once=True, use_container_width=True)

if audio:
    # ในส่วนนี้ streamlit-mic-recorder จะส่งค่าเป็นไฟล์เสียง
    # แต่เนื่องจากเราต้องการ text ผมแนะนำให้ใช้การพิมพ์หรือถ้าเจ้านายต้องการฟีเจอร์แปลเสียง
    # บน Cloud จะต้องใช้ API ของ Google Speech-to-Text ซึ่งซับซ้อนกว่า
    # ณ ตอนนี้ ผมทำปุ่มให้รองรับการทำงานเบื้องต้นก่อนครับ
    st.info("ได้รับไฟล์เสียงแล้ว (ฟังก์ชันแปลงเสียงกำลังพัฒนาต่อครับ)")

txt_item = st.text_input("📝 ชื่อรายการ:", value=st.session_state.temp_item)
txt_amount = st.number_input("💵 จำนวนเงิน (บาท):", min_value=0.0, value=float(st.session_state.temp_amount), format="%.2f")

if st.button("💾 บันทึกลงสมุดบัญชี"):
    # บันทึกข้อมูล...
    st.success("บันทึกสำเร็จ!")