from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from .scraper import fetch_raw_csv_data
from .transformer import transform_to_sensor_data

app = FastAPI(title="Buoy Sensor API")

def get_formatted_data() -> str:
    """データ取得と変換の共通処理"""
    raw_data = fetch_raw_csv_data()
    clean_data = transform_to_sensor_data(raw_data)
    return "\n".join(clean_data)

@app.get("/")
@app.get("/api")
def read_root():
    return {"message": "API is running. Access /api/sensor-data to get data."}

# 通常の想定パス
@app.get("/sensor-data", response_class=PlainTextResponse)
@app.get("/api/sensor-data", response_class=PlainTextResponse)
def get_sensor_data():
    return get_formatted_data()

# どんなパスでアクセスされても拾うフォールバック（デバッグ兼救済措置）
@app.get("/{full_path:path}")
def catch_all(full_path: str, request: Request):
    # URLの中に sensor-data が含まれていればデータを返す
    if "sensor-data" in full_path:
        return PlainTextResponse(get_formatted_data())
    
    return {
        "status": "404 Not Found",
        "requested_path": full_path,
        "full_url": str(request.url),
        "hint": "Access /api/sensor-data"
    }
