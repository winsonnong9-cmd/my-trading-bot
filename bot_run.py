import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import joblib
import requests  # ย้ายมาไว้ด้านบนสุดเพื่อความเป็นระเบียบของระบบ

# --- 1. เตรียมฟังก์ชันส่ง LINE ไว้ให้พร้อมใช้งาน ---
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
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code


# --- 2. ฟังก์ชันหลักของบอทเทรด AI ---
def run_my_bot():
    # 1. โหลดสมอง AI ที่เราเทรนไว้ขึ้นมาใช้งาน
    brain = joblib.load('trading_bot_brain.joblib')
    model = brain['model']
    features = brain['features']
    
    # 2. ดึงข้อมูลราคาสดล่าสุด
    ticker = "BTC-USD"
    live_data = yf.download(ticker, period="60d", interval="1d")
    
    # เคลียร์หัวตาราง MultiIndex
    if isinstance(live_data.columns, pd.MultiIndex):
        live_data.columns = live_data.columns.get_level_values(0)
        
    # 3. คำนวณอินดิเคเตอร์ให้เหมือนตอนเทรนเป๊ะๆ
    live_data.ta.ema(length=10, append=True)
    live_data.ta.ema(length=50, append=True)
    live_data.ta.rsi(length=14, append=True)
    live_data['Log_Volume'] = np.log(live_data['Volume'] + 1)
    live_data.ta.bbands(length=20, std=2, append=True)
    
    if isinstance(live_data.columns, pd.MultiIndex):
        live_data.columns = live_data.columns.get_level_values(0)
        
    # 4. ดึงข้อมูลของ "แท่งเทียนปัจจุบัน (แถวสุดท้าย)" ออกมาป้อนให้ AI
    current_market = live_data[features].tail(1)
    
    # เช็คว่ามีค่าว่างไหม
    if current_market.isnull().values.any():
        msg_error = "⚠️ ข้อมูลสดวันปัจจุบันยังไม่สมบูรณ์ ขอยกเลิกการทำงานรอบนี้"
        print(msg_error)
        send_line(msg_error) # ส่งแจ้งเตือนบอกใน LINE ด้วยว่าข้อมูลไม่สมบูรณ์
        return

    # 5. ให้ AI สแกนและตัดสินใจ
    prediction = model.predict(current_market)[0]
    
    print(f"--- [ผลการวิเคราะห์ตลาดสด] ---")
    
    # [จุดที่แก้ไข ✨] ประกาศตัวแปร result_text มารับข้อความตามเงื่อนไขอย่างถูกต้อง
    if prediction == 1:
        result_text = "🚀 AI วิเคราะห์แล้ว: สัญญาณเป็น 1 -> แนะนำให้ 'เข้าซื้อ' จุดนี้ได้เปรียบ!"
        # [จุดติดตั้ง API ในอนาคต] เช่น ccxt.create_market_buy_order()
    else:
        result_text = "🛑 AI วิเคราะห์แล้ว: สัญญาณเป็น 0 -> แนะนำให้ 'ถือเงินสดเงียบๆ' หรือปิดออเดอร์"
        # [จุดติดตั้ง API ในอนาคต] เช่น ccxt.create_market_sell_order()

    # พิมพ์แสดงผลบนหน้าจอ Cloud
    print(result_text)
    
    # ยิงข้อความแจ้งเตือนตรงเข้า LINE ส่วนตัวทันที!
    send_line(f"🤖 ผลการวิเคราะห์จาก Cloud วันนี้:\n{result_text}")


# --- 3. สั่งรันระบบ ---
if __name__ == "__main__":
    run_my_bot()