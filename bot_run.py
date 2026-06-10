import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import joblib

def run_my_bot():
    # 1. โหลดสมอง AI ที่เราเทรนไว้ขึ้นมาใช้งาน
    brain = joblib.load('trading_bot_brain.joblib')
    model = brain['model']
    features = brain['features']
    
    # 2. ดึงข้อมูลราคาสดล่าสุด (ดึงย้อนหลัง 60 วัน เพื่อให้พอคำนวณ EMA และ RSI ได้แม่นยำ)
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
    
    # เช็คว่ามีค่าว่างไหม (ถ้าข้อมูลสดดึงมาไม่ครบ ให้หยุดทำงานก่อน)
    if current_market.isnull().values.any():
        print("⚠️ ข้อมูลสดวันปัจจุบันยังไม่สมบูรณ์ ขอยกเลิกการทำงานรอบนี้")
        return

    # 5. ให้ AI สแกนและตัดสินใจ
    prediction = model.predict(current_market)[0]
    
    print(f"--- [ผลการวิเคราะห์ตลาดสด] ---")
    if prediction == 1:
        print("🚀 AI วิเคราะห์แล้ว: สัญญาณเป็น 1 -> แนะนำให้ 'เข้าซื้อ' จุดนี้ได้เปรียบ!")
        # [จุดติดตั้ง API] ในอนาคตคุณจะใส่คำสั่งยิงเข้า Exchange เช่น ccxt.create_market_buy_order() ตรงนี้
    else:
        print("🛑 AI วิเคราะห์แล้ว: สัญญาณเป็น 0 -> แนะนำให้ 'ถือเงินสดเงียบๆ' หรือปิดออเดอร์")
        # [จุดติดตั้ง API] ใส่คำสั่งขายตัดความเสี่ยง เช่น ccxt.create_market_sell_order() ตรงนี้

if __name__ == "__main__":
    run_my_bot()
import requests
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

# บรรทัดส่งท้าย: เรียกใช้งานฟังก์ชันส่งเข้า LINE 
# (แก้คำว่า result_text ให้ตรงกับตัวแปรที่เก็บข้อความสรุปของบอทคุณนะ)
send_line(f"🤖 ผลการวิเคราะห์จาก Cloud วันนี้:\n{result_text}")