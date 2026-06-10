import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import joblib
import requests

# --- 1. ฟังก์ชันส่ง LINE ---
def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    USER_ID = "U223dd700347973c0b206a79dfd1184fa"
    ACCESS_TOKEN = "XxhNYPMkVHUQeSxk2nL50VSaWgidP/tDwC+c5xpOkWI1y6ao/OwPe2wAKVjC5xSm1qiJm+XF1nmuMdA96DP0xByFGelK/xM48CBqeyuvPPVFt0Tr2QEUl2i6kXpC6ECsTegzpQw2e85wPMkl/rGUjgdB04t89/1O/w1cDnyilFU="
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    payload = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code

# --- 2. ฟังก์ชันหลักของบอทหุ้น ---
def run_my_bot():
    # 1. โหลดสมอง AI ของ TSMC ตัวใหม่ที่เราเพิ่งเทรนบนคลาวด์
    brain = joblib.load('tsmc_bot_brain.joblib') 
    model = brain['model']
    features = brain['features']
    
    # 2. ดึงข้อมูลสดล่าสุดของทั้ง 2 ตัว
    tsm_live = yf.download("TSM", period="60d", interval="1d")
    spx_live = yf.download("^GSPC", period="60d", interval="1d")
    
    # เคลียร์หัวตาราง MultiIndex
    for df in [tsm_live, spx_live]:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
    # 3. คำนวณอินดิเคเตอร์ฝั่ง S&P 500 (ตัวแม่)
    spx_live['SPX_RSI'] = ta.rsi(spx_live['Close'], length=14)
    spx_live['SPX_EMA50'] = ta.ema(spx_live['Close'], length=50)
    spx_live['SPX_Trend'] = (spx_live['Close'] > spx_live['SPX_EMA50']).astype(int)
    
    # 4. คำนวณอินดิเคเตอร์ฝั่ง TSMC (ตัวเล่น)
    tsm_live['TSM_RSI'] = ta.rsi(tsm_live['Close'], length=14)
    tsm_live['EMA_10'] = ta.ema(tsm_live['Close'], length=10)
    tsm_live['EMA_50'] = ta.ema(tsm_live['Close'], length=50)
    
    # 5. ฟิวชันรวมข้อมูลเข้าด้วยกันตาม วันที่
    features_from_spx = ['SPX_RSI', 'SPX_Trend']
    merged_live = tsm_live.join(spx_live[features_from_spx], how='inner')
    
    # 6. ดึงข้อมูลแท่งเทียนล่าสุด (แถวสุดท้าย) ออกมาวิเคราะห์
    current_market = merged_live[features].tail(1)
    
    # เช็คค่าว่าง
    if current_market.isnull().values.any():
        print("⚠️ ข้อมูลสดของวันนี้ยังไม่สมบูรณ์ ขอยกเลิกการทำงานรอบนี้")
        return

    # 7. ให้ AI ตัดสินใจ
    prediction = model.predict(current_market)[0]
    
    print(f"--- [ผลการวิเคราะห์ตลาดหุ้นสด TSMC] ---")
    if prediction == 1:
        result_text = "🚀 AI วิเคราะห์ TSMC แนะนำให้: 'เข้าซื้อ' (ภาพรวมตลาดและเทคนิคเป็นใจ)"
    else:
        result_text = "🛑 AI วิเคราะห์ TSMC แนะนำให้: 'ถือเงินสดเงียบๆ' หรือปิดออเดอร์เพื่อลดความเสี่ยง"

    print(result_text)
    
    # ส่งข้อความเข้า LINE
    send_line(f"🤖 ผลวิเคราะห์หุ้นคลาวด์วันนี้:\n{result_text}")

if __name__ == "__main__":
    run_my_bot()