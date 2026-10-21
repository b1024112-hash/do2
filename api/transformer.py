import struct
import math
from datetime import datetime, timezone, timedelta

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
        
        if "STAT:" in decoded_text or ("," in decoded_text and not hex_str.startswith(("3e", "3d", "3c", "3b", "3a", "39", "38", "37", "36", "35", "34", "33", "32", "31", "30"))):
            result["text_data"] = decoded_text
            return result

        if len(payload_bytes) >= 16:
            try:
                unpacked = struct.unpack('<ffff', payload_bytes[:16])
                lat = round(unpacked[0], 6)
                lon = round(unpacked[1], 6)
                temp = round(unpacked[2], 2)
                do_sat = round(unpacked[3], 2)

                if -100 <= temp <= 60 and -200 <= do_sat <= 500:
                    if lat > 1000:
                        deg_lat = int(lat / 100)
                        lat = round(deg_lat + ((lat - (deg_lat * 100)) / 60), 6)
                    if lon > 1000:
                        deg_lon = int(lon / 100)
                        lon = round(deg_lon + ((lon - (deg_lon * 100)) / 60), 6)

                    result["latitude"] = lat
                    result["longitude"] = lon
                    result["temperature"] = temp
                    result["do_saturation"] = do_sat
                    
                    if temp > -100 and do_sat > -100:
                        result["do_mg_l"] = calculate_do_mg_l(temp, do_sat)
                    return result
            except Exception:
                pass

        result["text_data"] = decoded_text
    except Exception:
        pass
        
    return result

def convert_to_jst(date_str: str, time_str: str) -> str:
    """UTC（Z）のタイムスタンプを日本時間（JST / UTC+9）に変換する"""
    try:
        # "2026-10-09", "06:30:02" のような文字列を結合してパース
        dt_utc = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        
        # 9時間を足して日本時間（JST）にする
        jst_timezone = timezone(timedelta(hours=9))
        dt_jst = dt_utc.astimezone(jst_timezone)
        
        # "2026-10-09T15:30:02+09:00" の形式で返す
        return dt_jst.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        # パースに失敗した場合はそのまま返す
        return f"{date_str} {time_str}"

def transform_to_sensor_data(raw_data: list[dict]) -> list[str]:
    """デコードした結果をカンマ区切りの文字列（日本時間表示）に変換する"""
    formatted_lines = []
    
    for item in raw_data:
        buoy_id = item.get('buoy_id', '')
        date = item.get('date', '')
        time = item.get('time', '')
        payload = item.get('payload', '')
        
        # タイムスタンプを日本時間（JST）に変換
        jst_datetime_str = convert_to_jst(date, time)
        
        # デコード実行
        decoded = decode_payload(payload)
        
        lat = decoded["latitude"] if decoded["latitude"] is not None else ""
        lon = decoded["longitude"] if decoded["longitude"] is not None else ""
        temp = decoded["temperature"] if decoded["temperature"] is not None else ""
        do_sat = decoded["do_saturation"] if decoded["do_saturation"] is not None else ""
        do_mg = decoded["do_mg_l"] if decoded["do_mg_l"] is not None else ""
        text = decoded["text_data"] if decoded["text_data"] is not None else ""
        
        if text:
            line = f"{buoy_id},{jst_datetime_str},{text}"
        else:
            line = f"{buoy_id},{jst_datetime_str},{lat},{lon},{temp},{do_sat},{do_mg}"
            
        formatted_lines.append(line)
        
    return formatted_lines