import struct
import math
import re

def calculate_do_mg_l(temp_c: float, do_saturation: float) -> float:
    """温度とDO飽和度から溶存酸素量(mg/L)を計算する"""
    if temp_c is None or do_saturation is None:
        return None
    try:
        T_k = temp_c + 273.15
        ln_Cstar = -139.34411 + (1.575701e5 / T_k) - (6.642308e7 / (T_k**2)) + (1.243800e10 / (T_k**3)) - (8.621949e11 / (T_k**4))
        do_sat_ml_l = math.exp(ln_Cstar)
        do_sat_mg_l = do_sat_ml_l * 1.42905
        return round(do_sat_mg_l * (do_saturation / 100.0), 2)
    except Exception:
        return None

def is_valid_coordinate(lat, lon) -> bool:
    """緯度経度が数値かつ0以外で正常な範囲にあるかチェック"""
    if lat is None or lon is None:
        return False
    try:
        lat_f, lon_f = float(lat), float(lon)
        if lat_f == 0.0 or lon_f == 0.0:
            return False
        return (-90 <= lat_f <= 90) and (-180 <= lon_f <= 180)
    except (ValueError, TypeError):
        return False

def decode_payload(hex_str: str) -> dict:
    """16進数ペイロードをデコードする"""
    result = {
        "latitude": None,
        "longitude": None,
        "temperature": None,
        "do_saturation": None,
        "do_mg_l": None,
        "text_data": None
    }
    
    try:
        payload_bytes = bytes.fromhex(hex_str)
        decoded_text = payload_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
        
        # 1. まずテキスト形式 "水温,DO飽和度" (例: "18.89,97.59") かどうかを厳密に判定
        text_match = re
