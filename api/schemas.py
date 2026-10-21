from pydantic import BaseModel
from typing import Optional

class SensorData(BaseModel):
    date: str          # 日時
    time: str          # 時刻
    raw_payload: str   # 元のData Payload
    latitude: Optional[float]    # 緯度
    longitude: Optional[float]   # 経度
    temperature: Optional[float] # 温度 (℃)
    do_saturation: Optional[float] # 溶存酸素飽和度 (%)
    do_mg_l: Optional[float]     # 計算された溶存酸素量 (mg/L)
    text_data: Optional[str]     # 文字列データ（ある場合）