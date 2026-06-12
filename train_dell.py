import yfinance as yf
import pandas as pd
import pandas_ta as ta
import joblib
from sklearn.ensemble import RandomForestClassifier

# ดึงข้อมูลย้อนหลัง 10 ปี
dell_data = yf.download("DELL", start="2016-01-01", end="2026-06-01")
spx_data = yf.download("^GSPC", start="2016-01-01", end="2026-06-01")

for df in [dell_data, spx_data]:
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

# คำนวณอินดิเคเตอร์
dell_data['DELL_RSI'] = ta.rsi(dell_data['Close'], length=14)
dell_data['EMA_10'] = ta.ema(dell_data['Close'], length=10)
dell_data['EMA_50'] = ta.ema(dell_data['Close'], length=50)
spx_data['SPX_RSI'] = ta.rsi(spx_data['Close'], length=14)
spx_data['SPX_EMA50'] = ta.ema(spx_data['Close'], length=50)
spx_data['SPX_Trend'] = (spx_data['Close'] > spx_data['SPX_EMA50']).astype(int)

df = dell_data.join(spx_data[['SPX_RSI', 'SPX_Trend']], how='inner')

# 🔥 จุดสำคัญ: มองอนาคตอีก 7 วันข้างหน้าของ DELL
df['Target'] = (df['Close'].shift(-7) > df['Close']).astype(int)

features = ['DELL_RSI', 'EMA_10', 'EMA_50', 'SPX_RSI', 'SPX_Trend']
df = df.dropna(subset=features + ['Target'])

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(df[features], df['Target'])

joblib.dump({'model': model, 'features': features}, 'dell_bot_brain.joblib')
print("✨ เซฟไฟล์ 'dell_bot_brain.joblib' สำเร็จ!")