from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from .scraper import fetch_raw_csv_data
from .transformer import transform_to_sensor_data

app = FastAPI(title="Buoy Sensor API")

def fetch_and_format_data():
    """データを取得してテキスト化する共通処理"""
    raw_data = fetch_raw_csv_data()
    clean_data = transform_to_sensor_data(raw_data)
    return "\n".join(clean_data)

# URLがルート（/）の場合
@app.get("/", response_class=PlainTextResponse)
def read_root():
    return fetch_and_format_data()

# URLに何らかのパス（/api/sensor-data や /api/index.py など）がついている場合
@app.get("/{path_name:path}", response_class=PlainTextResponse)
def catch_all(path_name: str):
    return fetch_and_format_data()
