import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import joblib
import requests
import matplotlib.pyplot as plt  # 🎨 1. เพิ่มตัววาดกราฟ

# --- 1. ฟังก์ชันส่ง LINE (ข้อความตัวหนังสือ - ของเดิมของคุณ) ---
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

# --- 2. ฟังก์ชันส่ง LINE (ส่งรูปภาพ - เพิ่มเข้ามาใหม่) ---
def send_line_image(image_url):
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
                "type": "image",
                "originalContentUrl": image_url,  # ลิงก์รูปภาพตัวเต็ม
                "previewImageUrl": image_url      # ลิงก์รูปภาพตัวอย่างในห้องแชท
            }
        ]
    }
    requests.post(url, json=payload, headers=headers)

# --- 3. ฟังก์ชันจำลองการอัปโหลดรูปขึ้น Cloud Hosting ---
def upload_image_to_cloud(image_path):
    # ยินดีต้อนรับสู่โลกความจริง: ตรงนี้ในอนาคตเราจะต้องเขียนโค้ดเชื่อมต่อ API เช่น Imgur หรือ Supabase
    # เพื่ออัปโหลดไฟล์ในเครื่องคลาวด์ขึ้นไปแปลงเป็นลิงก์ https://...
    # ตอนนี้สมมติลิงก์จำลองขึ้นมาทดสอบระบบก่อนครับ
    print(f"☁️ อัปโหลดไฟล์ {image_path} ขึ้นระบบคลาวด์เซิร์ฟเวอร์สำเร็จ")
    return "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800" # ลิงก์รูปกราฟตัวอย่างชั่วคราว

# --- 4. ฟังก์ชันหลักเวอร์ชันอัปเกรด (Multi-Asset + Chart) ---
def run_my_bot():
    # 🎯 ตั้งค่ารายชื่อหุ้นใน Portfolio หรือ Watchlist ที่เราสนใจ
    my_portfolio = ["TSM", "DELL"] 
    
    # วิ่งดึงข้อมูลดัชนีแม่ S&P 500 (`^GSPC`) มารอไว้ก่อนครั้งเดียว (ไม่ต้องดึงซ้ำในลูป)
    spx_live = yf.download("^GSPC", period="60d", interval="1d")
    if isinstance(spx_live.columns, pd.MultiIndex):
        spx_live.columns = spx_live.columns.get_level_values(0)
        
    spx_live['SPX_RSI'] = ta.rsi(spx_live['Close'], length=14)
    spx_live['SPX_EMA50'] = ta.ema(spx_live['Close'], length=50)
    spx_live['SPX_Trend'] = (spx_live['Close'] > spx_live['SPX_EMA50']).astype(int)
    features_from_spx = ['SPX_RSI', 'SPX_Trend']

    # 🔄 เริ่มต้นลูปตรวจเช็คหุ้นทีละตัวในพอร์ต
    for ticker in my_portfolio:
        print(f"🔍 กำลังประมวลผลหุ้น: {ticker}")
        
        try:
            # 1. โหลดสมอง AI แยกตามชื่อหุ้น (เช่น tsm_bot_brain.joblib, dell_bot_brain.joblib)
            brain_name = f"{ticker.lower()}_bot_brain.joblib"
            brain = joblib.load(brain_name) 
            model = brain['model']
            features = brain['features']
            
            # 2. ดึงข้อมูลสดของหุ้นตัวนั้นๆ
            stock_live = yf.download(ticker, period="60d", interval="1d")
            if isinstance(stock_live.columns, pd.MultiIndex):
                stock_live.columns = stock_live.columns.get_level_values(0)
            
            # 3. คำนวณอินดิเคเตอร์เทคนิคอลของหุ้นตัวนั้น
            stock_live[f'{ticker}_RSI'] = ta.rsi(stock_live['Close'], length=14)
            stock_live['EMA_10'] = ta.ema(stock_live['Close'], length=10)
            stock_live['EMA_50'] = ta.ema(stock_live['Close'], length=50)
            
            # 4. ฟิวชันรวมร่างกับดัชนีแม่ S&P 500
            merged_live = stock_live.join(spx_live[features_from_spx], how='inner')
            
            # 5. สั่ง Matplotlib พล็อตกราฟราคาหุ้นเก็บไว้เป็นไฟล์รูปภาพ
            plt.figure(figsize=(10, 5))
            plt.plot(merged_live.index, merged_live['Close'], label=f'{ticker} Close Price', color='blue')
            plt.title(f'{ticker} Daily Technical Chart')
            plt.xlabel('Date')
            plt.ylabel('Price (USD)')
            plt.grid(True)
            plt.legend()
            
            image_filename = f"{ticker.lower()}_chart.png"
            plt.savefig(image_filename, bbox_inches='tight')  # เซฟรูปเก็บไว้ในเครื่องคลาวด์
            plt.close()  # ปิดออบเจกต์รูปภาพเพื่อประหยัดแรมเซิร์ฟเวอร์
            
            # 6. ส่งรูปไปแปลงเป็น URL สาธารณะ
            public_image_url = upload_image_to_cloud(image_filename)
            
            # 7. ดึงข้อมูลวันล่าสุดส่งให้ AI ทำนายผล (มองทิศทาง)
            current_market = merged_live[features].tail(1)
            
            if current_market.isnull().values.any():
                print(f"⚠️ ข้อมูลสดของหุ้น {ticker} วันนี้ไม่สมบูรณ์ ข้ามไปตัวถัดไป")
                continue
                
            prediction = model.predict(current_market)[0]
            
            # แปลผลลัพธ์การคาดคะเน (ถ้าเทรนโมเดลมองข้าม 7 วันมาแล้ว ข้อความนี้จะตอบโจทย์มาก)
            if prediction == 1:
                result_text = f"🚀 [หุ้น {ticker}] แนวโน้มอีก 7 วันข้างหน้า: 'สดใส' มีโอกาสปรับตัวขึ้น แนะนำถือต่อหรือพิจารณาซื้อเพิ่ม"
            else:
                result_text = f"🛑 [หุ้น {ticker}] แนวโน้มอีก 7 วันข้างหน้า: 'ความเสี่ยงสูง' หรือตลาดชะลอตัว แนะนำถือเงินสดนิ่งๆ เพื่อลดความเสี่ยง"
                
            print(result_text)
            
            # 8. ยิงแจ้งเตือนเข้า LINE รัวๆ 2 คอมโบ (ข้อความวิเคราะห์ + รูปกราฟประกอบ)
            send_line(f"🤖 ผลวิเคราะห์จากพอร์ตจำลองวันนี้:\n{result_text}")
            send_line_image(public_image_url)
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดกับหุ้น {ticker}: {e}")

if __name__ == "__main__":
    run_my_bot()