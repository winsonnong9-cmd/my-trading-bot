import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier # ใช้ RandomForest ตัวเก่งของคุณ

def train_my_ai():
    print("📥 1. กำลังดึงข้อมูลย้อนหลัง 10 ปี จาก Yahoo Finance...")
    # ดึงข้อมูลยาวๆ เพื่อให้ AI เห็นพฤติกรรมหุ้นครบทุกสภาวะตลาด
    tsm_data = yf.download("TSM", start="2016-01-01", end="2026-06-01")
    spx_data = yf.download("^GSPC", start="2016-01-01", end="2026-06-01")

    # เคลียร์หัวตารางกรณีเจอปัญหา MultiIndex
    for df in [tsm_data, spx_data]:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

    print("📊 2. กำลังคำนวณสารอาหาร (Features) ให้ AI...")
    # คำนวณฝั่ง TSMC
    tsm_data['TSM_RSI'] = ta.rsi(tsm_data['Close'], length=14)
    tsm_data['EMA_10'] = ta.ema(tsm_data['Close'], length=10)
    tsm_data['EMA_50'] = ta.ema(tsm_data['Close'], length=50)

    # คำนวณฝั่ง S&P 500 (ตัวแม่คุมตลาด)
    spx_data['SPX_RSI'] = ta.rsi(spx_data['Close'], length=14)
    spx_data['SPX_EMA50'] = ta.ema(spx_data['Close'], length=50)
    spx_data['SPX_Trend'] = (spx_data['Close'] > spx_data['SPX_EMA50']).astype(int)

    print("🔗 3. กำลังฟิวชันรวมข้อมูลของทั้งคู่เข้าด้วยกัน...")
    # ดึงเฉพาะคอลัมน์ที่เราต้องการจาก S&P 500 มารวมกับ TSMC
    spx_features = ['SPX_RSI', 'SPX_Trend']
    df = tsm_data.join(spx_data[spx_features], how='inner')

    print("🎯 4. กำลังสร้างเฉลย (Target) ให้ AI เรียนรู้...")
    # สร้างโจทย์: ถ้าวันพรุ่งนี้ราคาปิดสูงกว่าวันนี้ ให้เฉลยเป็น 1 (ขึ้น) ถ้าไม่ใช่ให้เป็น 0 (ลง/นิ่ง)
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

    # กำหนดรายชื่อคอลัมน์ที่ต้องการให้ AI ใช้คิด (ต้องตรงกับใน bot_run.py)
    features = ['TSM_RSI', 'EMA_10', 'EMA_50', 'SPX_RSI', 'SPX_Trend']

    # ลบแถวที่มีค่าว่าง (NaN) ทิ้งไปเพื่อไม่ให้โมเดลเอเรอร์
    df = df.dropna(subset=features + ['Target'])

    # แยกโจทย์ (X) และ เฉลย (y)
    X = df[features]
    y = df['Target']

    print("🧠 5. AI กำลังทำข้อสอบเก่าเพื่อเรียนรู้แพทเทิร์น...")
    # สร้างตัวโมเดลและสั่งเทรน (Fit)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    print("💾 6. เสร็จสิ้น! กำลังเซฟสมอง AI ลงไฟล์...")
    # มัดแพ็คใส่ Dictionary เก็บทั้งตัวนางแบบ (Model) และชื่อคอลัมน์ (Features)
    brain_packet = {
        'model': model,
        'features': features
    }
    
    # เซฟออกมาเป็นไฟล์สมอง TSMC
    joblib.dump(brain_packet, 'tsmc_bot_brain.joblib')
    print("✨ เซฟไฟล์ 'tsmc_bot_brain.joblib' เรียบร้อยพร้อมใช้งานแล้วครับ!")

if __name__ == "__main__":
    train_my_ai()