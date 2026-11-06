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
        text_match = re.match(r"^(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)$", decoded_text)
        if text_match:
            temp = float(text_match.group(1))
            do_sat = float(text_match.group(2))
            
            result["temperature"] = temp
            result["do_saturation"] = do_sat
            result["do_mg_l"] = calculate_do_mg_l(temp, do_sat)
            return result

        # 2. バイナリ(float x4)としてデコードを試みる
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
                    
                    # センサーデータとして正常ならここで返す（テキスト判定には進まない）
                    return result
            except Exception:
                pass

        # 3. floatとして解釈できなかった(または範囲外だった)場合のみテキストとして判定する
        if "STAT:" in decoded_text or "," in decoded_text:
            result["text_data"] = decoded_text

    except Exception:
        pass
        
    return result

def transform_to_sensor_data(raw_data: list[dict]) -> list[str]:
    """デコードした結果をカンマ区切りの文字列に変換する"""
    formatted_lines = []
    
    # ブイごとの直近の正常な位置情報を記録する辞書
    last_known_locations = {}
    
    for item in raw_data:
        buoy_id = item.get('buoy_id', '')
        date = item.get('date', '')
        time = item.get('time', '')
        payload = item.get('payload', '')
        
        # タイムスタンプをそのまま結合
        datetime_str = f"{date} {time}".strip()
        
        # デコード実行
        decoded = decode_payload(payload)
        
        lat = decoded["latitude"]
        lon = decoded["longitude"]
        
        # 正常な緯度経度がある場合は記憶を更新、無い場合は直前のデータから引き継ぐ
        if is_valid_coordinate(lat, lon):
            last_known_locations[buoy_id] = (lat, lon)
        elif buoy_id in last_known_locations:
            lat, lon = last_known_locations[buoy_id]
        else:
            lat, lon = "", ""
        
        temp = decoded["temperature"] if decoded["temperature"] is not None else ""
        do_sat = decoded["do_saturation"] if decoded["do_saturation"] is not None else ""
        do_mg = decoded["do_mg_l"] if decoded["do_mg_l"] is not None else ""
        text = decoded["text_data"] if decoded["text_data"] is not None else ""
        
        if text:
            line = f"{buoy_id},{datetime_str},{text}"
        else:
            line = f"{buoy_id},{datetime_str},{lat},{lon},{temp},{do_sat},{do_mg}"
            
        formatted_lines.append(line)
        
    return formatted_lines
