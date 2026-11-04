import struct
import math
import re
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
    """16進数ペイロードをデコードする（テキスト形式・バイナリ形式両対応）"""
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
        # ^-?\d+(?:\.\d+)? : 整数または小数の数値
        text_match = re.match(r"^(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)$", decoded_text)
        
        if text_match:
            temp = float(text_match.group(1))
            do_sat = float(text_match.group(2))
            
            result["temperature"] = temp
            result["do_saturation"] = do_sat
            result["do_mg_l"] = calculate_do_mg_l(temp, do_sat)
            # CSV出力時にテキストとして出力されないよう text_data はセットしない、もしくは別途扱う
            return result

        # 2. テキスト形式でなければ、バイナリ形式 (float x 4) としてパースを試みる
        if len(payload_bytes) >= 16:
            try:
                unpacked = struct.unpack('<ffff', payload_bytes[:16])
                lat = round(unpacked[0], 6)
                lon = round(unpacked[1], 6)
                temp = round(unpacked[2], 2)
                do_sat = round(unpacked[3], 2)

                # 値が現実的なセンサーデータの範囲内かチェック (ゴミデータとの切り分け)
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

        # 3. どちらの形式にも当てはまらない場合 (STAT:等のログ文字列)
        if "STAT:" in decoded_text or "," in decoded_text:
            result["text_data"] = decoded_text

    except Exception:
        pass
        
    return result

def convert_to_jst(date_str: str, time_str: str) -> str:
    """UTC（Z）のタイムスタンプを日本時間（JST / UTC+9）に変換する"""
    try:
        dt_utc = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        
        jst_timezone = timezone(timedelta(hours=9))
        dt_jst = dt_utc.astimezone(jst_timezone)
        
        return dt_jst.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return f"{date_str} {time_str}"

def transform_to_sensor_data(raw_data: list[dict]) -> list[str]:
    """デコードした結果をカンマ区切りの文字列（日本時間表示）に変換する"""
    formatted_lines = []
    
    for item in raw_data:
        buoy_id = item.get('buoy_id', '')
        date = item.get('date', '')
        time = item.get('time', '')
        payload = item.get('payload', '')
        
        jst_datetime_str = convert_to_jst(date, time)
        decoded = decode_payload(payload)
        
        lat = decoded["latitude"] if decoded["latitude"] is not None else ""
        lon = decoded["longitude"] if decoded["longitude"] is not None else ""
        temp = decoded["temperature"] if decoded["temperature"] is not None else ""
        do_sat = decoded["do_saturation"] if decoded["do_saturation"] is not None else ""
        do_mg = decoded["do_mg_l"] if decoded["do_mg_l"] is not None else ""
        text = decoded["text_data"] if decoded["text_data"] is not None else ""
        
        # テキストデータ（STATなど）が入っている場合はそれを出力し、
        # そうでない場合は水温やDOなどの数値データをカンマ区切りで出力する
        if text:
            line = f"{buoy_id},{jst_datetime_str},{text}"
        else:
            line = f"{buoy_id},{jst_datetime_str},{lat},{lon},{temp},{do_sat},{do_mg}"
            
        formatted_lines.append(line)
        
    return formatted_lines

        print(line)
