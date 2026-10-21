from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from .scraper import fetch_raw_csv_data
from .transformer import transform_to_sensor_data

app = FastAPI(title="Buoy Sensor API")

@app.get("/")
def read_root():
    return {"message": "API is running. Access /api/sensor-data to get data."}

# デバッグ用：何が取得できているかJSONでそのまま返す
@app.get("/api/sensor-data")
def get_sensor_data():
    raw_data = fetch_raw_csv_data()
    
    # もし raw_data が空なら、ここでわかる
    if not raw_data:
        return {"debug": "raw_data is empty", "raw_data": raw_data}
        
    clean_data = transform_to_sensor_data(raw_data)
    
    # もし clean_data が空なら、ここでわかる
    if not clean_data:
        return {"debug": "clean_data is empty", "raw_data_sample": raw_data[:5]}
        
    return {"debug": "success", "clean_data_sample": clean_data[:5]}
