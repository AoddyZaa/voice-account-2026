import streamlit as st
import pandas as pd
from datetime import datetime
import speech_recognition as sr
import re
import io
import os

# 1. ตั้งค่าหน้าจอ UI
st.set_page_config(page_title="Voice Expense 2026", layout="centered")

st.title("📖 สมุดบัญชีดิจิทัล (เวอร์ชันทศนิยมเป๊ะ + ระบบล็อกรหัสผ่าน)")
st.write("ข้อมูลเซฟลงคอมฯ ถาวร และมีระบบป้องกันคนอื่นมาแอบลบข้อมูล")

# 💾 🛠️ ระบบจัดการฐานข้อมูลไฟล์
DB_FILE = "expense_database.csv"
BACKUP_FILE = "expense_database_backup.csv"  # ไฟล์สำรองฉุกเฉินกันพลาด

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df = df.astype({"รายรับ (บาท)": "float64", "รายจ่าย (บาท)": "float64"})
            return df
        except:
            pass
    df = pd.DataFrame(columns=["วัน-เวลา บันทึก", "เดือน-ปี", "รายการ", "รายรับ (บาท)", "รายจ่าย (บาท)", "ประเภทดิบ"])
    return df.astype({"รายรับ (บาท)": "float64", "รายจ่าย (บาท)": "float64"})

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# โหลดข้อมูล
if "expense_data" not in st.session_state:
    st.session_state.expense_data = load_data()

# ส่วนพักข้อมูลสำหรับ 3 ขยัก
if "temp_item" not in st.session_state:
    st.session_state.temp_item = ""
if "temp_amount" not in st.session_state:
    st.session_state.temp_amount = 0.0

# ฟังก์ชันฟังเสียงภาษาไทย
def web_listen_voice_calm():
    r = sr.Recognizer()
    r.energy_threshold = 40       
    r.pause_threshold = 2.0        
    r.non_speaking_duration = 0.8  
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=0.8)
            audio = r.listen(source, timeout=8, phrase_time_limit=10)
            text = r.recognize_google(audio, language="th-TH")
            return text
        except:
            return ""

# ฟังก์ชันแปลงตัวเลขทศนิยม
def parse_thai_number_decimal(text):
    text_clean = text.replace(",", "").replace("บาท", "").strip()
    if "จุด" in text_clean:
        parts = text_clean.split("จุด")
        main_part, sub_part = parts[0].strip(), parts[1].strip()
        main_val = float("".join(re.findall(r'\d+', main_part))) if "".join(re.findall(r'\d+', main_part)) else float(parse_pure_thai_text(main_part))
        sub_val = float("0." + "".join(re.findall(r'\d+', sub_part))) if "".join(re.findall(r'\d+', sub_part)) else (parse_pure_thai_text(sub_part) / 100.0)
        return main_val + sub_val
    decimal_match = re.search(r'\d+\.\d+', text_clean)
    if decimal_match: return float(decimal_match.group())
    if text_clean.isdigit(): return float(text_clean)
    all_digits = "".join(re.findall(r'\d+', text_clean))
    if all_digits: return float(all_digits)
    return float(parse_pure_thai_text(text_clean))

def parse_pure_thai_text(text_clean):
    th_digits = {"ศูนย์": 0, "หนึ่ง": 1, "สอง": 2, "สาม": 3, "สี่": 4, "ห้า": 5, "หก": 6, "เจ็ด": 7, "แปด": 8, "เก้า": 9, "เอ็ด": 1}
    total, current_group = 0, 0
    tokens = re.findall(r'(สอง|สาม|สี่|ห้า|หก|เจ็ด|แปด|เก้า|หนึ่ง|ศูนย์|เอ็ด|สิบ|ร้อย|พัน|หมื่น|แสน|ล้าน)', text_clean)
    for token in tokens:
        if token in th_digits: current_group = th_digits[token]
        elif token == "สิบ":
            if current_group == 0: current_group = 1
            total += current_group * 10; current_group = 0
        elif token == "ร้อย":
            if current_group == 0: current_group = 1
            total += current_group * 100; current_group = 0
        elif token == "พัน":
            if current_group == 0: current_group = 1
            total += current_group * 1000; current_group = 0
    total += current_group
    return total

# -------------------------------------------------------------------
# 📝 ขั้นตอนการบันทึกแบบ 3 ขยัก
# -------------------------------------------------------------------
st.subheader("📝 ขั้นตอนการบันทึก")

chosen_type = st.radio(
    "🟢 ขยักที่ 1: เลือกประเภทของเงินที่จะป้อน:",
    options=["เงินคงเหลือยกมา", "รายรับ", "รายจ่าย"],
    index=1,
    horizontal=True
)

st.divider()
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🎙️ 2. กดพูดชื่อรายการ", use_container_width=True):
        with st.spinner("กำลังฟังชื่อรายการ..."):
            voice_res = web_listen_voice_calm()
            if voice_res: st.session_state.temp_item = voice_res
            else: st.error("ไม่ได้ยินเสียงชื่อรายการครับ")

txt_item = st.text_input("📝 ชื่อรายการที่ได้ยิน:", value=st.session_state.temp_item)
st.session_state.temp_item = txt_item

with col_btn2:
    disabled_status = False if txt_item else True
    if st.button("💵 3. กดพูดจำนวนเงิน (พูดเศษสตางค์ได้)", use_container_width=True, disabled=disabled_status):
        with st.spinner("กำลังฟังจำนวนเงิน..."):
            voice_res = web_listen_voice_calm()
            if voice_res: st.session_state.temp_amount = parse_thai_number_decimal(voice_res)
            else: st.error("ไม่ได้ยินเสียงจำนวนเงินครับ")

txt_amount = st.number_input(
    "💵 จำนวนเงิน (บาท):", 
    min_value=0.0, 
    value=float(st.session_state.temp_amount),
    format="%.2f",
    step=0.01
)
st.session_state.temp_amount = txt_amount

if st.button("💾 บันทึกลงสมุดบัญชี", use_container_width=True, type="primary", disabled=not txt_item):
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M")
    month_year = now.strftime("%m/%Y")
    
    val_income = 0.0
    val_expense = 0.0
    
    if chosen_type == "เงินคงเหลือยกมา" or chosen_type == "รายรับ":
        val_income = float(st.session_state.temp_amount)
    else:
        val_expense = float(st.session_state.temp_amount)
        
    new_row = pd.DataFrame([{
        "วัน-เวลา บันทึก": current_time, 
        "เดือน-ปี": month_year,
        "รายการ": st.session_state.temp_item, 
        "รายรับ (บาท)": val_income, 
        "รายจ่าย (บาท)": val_expense,
        "ประเภทดิบ": chosen_type
    }])
    
    st.session_state.expense_data = pd.concat([st.session_state.expense_data, new_row], ignore_index=True)
    save_data(st.session_state.expense_data)
    
    st.session_state.temp_item = ""
    st.session_state.temp_amount = 0.0
    st.rerun()

st.divider()

# -------------------------------------------------------------------
# 📅 ตารางสรุปแบบสมุดธนาคาร
# -------------------------------------------------------------------
st.subheader("📊 สมุดบัญชีประจำเดือน")

if not st.session_state.expense_data.empty:
    unique_months = st.session_state.expense_data["เดือน-ปี"].unique().tolist()
    current_month_str = datetime.now().strftime("%m/%Y")
    if current_month_str not in unique_months:
        unique_months.append(current_month_str)
    
    selected_month = st.selectbox("📅 เลือกเดือนที่ต้องการดูรายงาน:", options=sorted(unique_months, reverse=True))
    
    filtered_df = st.session_state.expense_data[st.session_state.expense_data["เดือน-ปี"] == selected_month].copy()
    filtered_df = filtered_df.reset_index(drop=True)
    
    running_balance = []
    current_bal = 0.0
    for idx, row in filtered_df.iterrows():
        current_bal += float(row["รายรับ (บาท)"]) - float(row["รายจ่าย (บาท)"])
        running_balance.append(current_bal)
        
    filtered_df["ยอดคงเหลือสะสม (บาท)"] = running_balance
    display_df = filtered_df[["วัน-เวลา บันทึก", "รายการ", "รายรับ (บาท)", "รายจ่าย (บาท)", "ยอดคงเหลือสะสม (บาท)"]]
    
    edited_df = st.data_editor(
        display_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "รายรับ (บาท)": st.column_config.NumberColumn("รายรับ (บาท)", format="%.2f"),
            "รายจ่าย (บาท)": st.column_config.NumberColumn("รายจ่าย (บาท)", format="%.2f"),
            "ยอดคงเหลือสะสม (บาท)": st.column_config.NumberColumn("ยอดคงเหลือสะสม (บาท)", format="%.2f")
        }
    )
    
    other_months_df = st.session_state.expense_data[st.session_state.expense_data["เดือน-ปี"] != selected_month]
    
    updated_current_month = []
    for idx, row in edited_df.iterrows():
        raw_type = "รายรับ" if row["รายรับ (บาท)"] > 0 else "รายจ่าย"
        if idx < len(filtered_df):
            raw_type = filtered_df.loc[idx, "ประเภทดิบ"]
            
        updated_current_month.append({
            "วัน-เวลา บันทึก": row["วัน-เวลา บันทึก"],
            "เดือน-ปี": selected_month,
            "รายการ": row["รายการ"],
            "รายรับ (บาท)": float(row["รายรับ (บาท)"]),
            "รายจ่าย (บาท)": float(row["รายจ่าย (บาท)"]),
            "ประเภทดิบ": raw_type
        })
        
    if st.button("🔄 อัปเดตการแก้ไขตารางลงไฟล์"):
        new_month_df = pd.DataFrame(updated_current_month)
        final_df = pd.concat([other_months_df, new_month_df], ignore_index=True)
        st.session_state.expense_data = final_df
        save_data(final_df)
        st.success("บันทึกการแก้ไขลงฐานข้อมูลเรียบร้อยแล้วครับ!")
        st.rerun()

    initial_balance = filtered_df[filtered_df["ประเภทดิบ"] == "เงินคงเหลือยกมา"]["รายรับ (บาท)"].sum()
    pure_income = filtered_df[filtered_df["ประเภทดิบ"] == "รายรับ"]["รายรับ (บาท)"].sum()
    total_expense = filtered_df["รายจ่าย (บาท)"].sum()
    net_wallet = (initial_balance + pure_income) - total_expense
    
    c1, c2, c3 = st.columns(3)
    c1.metric(label="🔵 เงินยกมาต้นเดือน", value=f"{initial_balance:,.2f} บาท")
    c2.metric(label="🟢 รายรับสะสมเดือนนี้", value=f"{pure_income:,.2f} บาท")
    c3.metric(label="🔴 รายจ่ายรวมเดือนนี้", value=f"{total_expense:,.2f} บาท")
    
    st.divider()
    st.metric(label="💰 ยอดเงินคงเหลือสุทธิ (ยกไปเดือนหน้า)", value=f"{net_wallet:,.2f} บาท")

# -------------------------------------------------------------------
# 🔐 ระบบความปลอดภัยขั้นสูง: ลบข้อมูล/ล้างปีเก่า (มีรหัสล็อก)
# -------------------------------------------------------------------
st.divider()
st.subheader("⚙️ โหมดผู้ดูแลระบบ (Admin Only)")

admin_mode = st.checkbox("🔓 เปิดโหมดจัดการข้อมูลระดับสูง (สำหรับเจ้านายเท่านั้น)")

if admin_mode:
    # รหัสผ่านสำหรับเจ้านาย (สามารถเปลี่ยนตรงคำว่า "1234" เป็นรหัสที่ต้องการได้เลยครับ)
    password = st.text_input("🔑 กรุณาใส่รหัสผ่านเพื่อเข้าถึงคำสั่งลบ:", type="password")
    
    if password == "1234":
        st.success("รหัสผ่านถูกต้อง ยินดีต้อนรับครับเจ้านาย!")
        
        col_del1, col_del2 = st.columns(2)
        
        with col_del1:
            if st.button("🗑️ ลบเฉพาะเดือนที่เลือกด้านบน", use_container_width=True, type="secondary"):
                if not st.session_state.expense_data.empty:
                    # สำรองข้อมูลไว้ในไฟล์ Backup เผื่อกดพลาด
                    st.session_state.expense_data.to_csv(BACKUP_FILE, index=False)
                    
                    # ลบข้อมูลเดือนที่เลือกออก
                    clean_df = st.session_state.expense_data[st.session_state.expense_data["เดือน-ปี"] != selected_month]
                    st.session_state.expense_data = clean_df
                    save_data(clean_df)
                    st.warning(f"ลบข้อมูลของเดือน {selected_month} เรียบร้อยแล้วครับ!")
                    st.rerun()
                    
        with col_del2:
            if st.button("🚨 ล้างฐานข้อมูลทั้งหมด (ขึ้นปีใหม่)", use_container_width=True, type="primary"):
                # สำรองข้อมูลไว้ในไฟล์ Backup เผื่อกดพลาด
                st.session_state.expense_data.to_csv(BACKUP_FILE, index=False)
                
                # ล้างทุกอย่างเป็นตารางเปล่า
                empty_df = pd.DataFrame(columns=["วัน-เวลา บันทึก", "เดือน-ปี", "รายการ", "รายรับ (บาท)", "รายจ่าย (บาท)", "ประเภทดิบ"])
                empty_df = empty_df.astype({"รายรับ (บาท)": "float64", "รายจ่าย (บาท)": "float64"})
                st.session_state.expense_data = empty_df
                save_data(empty_df)
                st.error("ล้างฐานข้อมูลทั้งหมดเรียบร้อยแล้ว! (ระบบสร้างไฟล์สำรองฉุกเฉินไว้ให้แล้วครับ)")
                st.rerun()
                
        # ปุ่มกู้คืนฉุกเฉิน (จะโผล่มาเมื่อมีไฟล์สำรอง)
        if os.path.exists(BACKUP_FILE):
            st.write("---")
            if st.button("🔄 🚨 กู้คืนข้อมูลฉุกเฉิน (Undo จากการกดลบล่าสุด)", use_container_width=True):
                backup_df = pd.read_csv(BACKUP_FILE)
                st.session_state.expense_data = backup_df
                save_data(backup_df)
                st.success("กู้คืนข้อมูลทั้งหมดกลับมาเรียบร้อยแล้วครับเจ้านาย! ปลอดภัยหายห่วง")
                st.rerun()
    elif password != "":
        st.error("❌ รหัสผ่านไม่ถูกต้องครับเจ้านาย!")