import schedule
import time
import subprocess
from datetime import datetime

def job():
    print(f"\n--- ⏰ ตื่นมาเทรดรอบเช้า: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    # สั่งให้เรียกไฟล์ bot_run.py ขึ้นมาทำงาน
    subprocess.run(["python", "bot_run.py"])
    print("--- 💤 เทรดเสร็จแล้ว กลับไปนอนรอพรุ่งนี้ ---")

# ตั้งเวลาปลุก 00:01 น. เวลา UTC (ซึ่งจะตรงกับเวลา 07:01 น. เช้าประเทศไทยเป๊ะ)
schedule.every().day.at("00:01").do(job)

print("🚀 ระบบเฝ้าเวร (UTC Time) ทำงานแล้ว! บอทจะตื่นมาสแกนตลาดทุกๆ 07:01 น. เวลาไทย")

# ลูปอมตะให้ระบบตื่นมาเช็คนาฬิกาทุกๆ 1 นาที
while True:
    schedule.run_pending()
    time.sleep(60)