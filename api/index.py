from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from .scraper import fetch_raw_csv_data
from .transformer import transform_to_sensor_data

app = FastAPI(title="Buoy Sensor API")

# / と /api の両方に対応
@app.get("/")
@app.get("/api")
def read_root():
    return {"message": "API is running. Access /api/sensor-data to get data."}

# /sensor-data と /api/sensor-data の両方に対応
@app.get("/sensor-data", response_class=PlainTextResponse)
@app.get("/api/sensor-data", response_class=PlainTextResponse)
def get_sensor_data():
    """デコードされたデータをカンマ区切りのテキスト形式で返す"""
    raw_data = fetch_raw_csv_data()
    clean_data = transform_to_sensor_data(raw_data)
    
    return "\n".join(clean_data)
