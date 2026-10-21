import requests
import csv
from io import StringIO

# 作成した settings.py から API_URL をインポートする
from .settings import API_URL

def fetch_raw_csv_data() -> list[dict]:
    """URLからCSVテキストを取得し、辞書のリストとして抽出する"""
    
    # 直書きではなく、settings からインポートした変数を使う
    response = requests.get(API_URL, timeout = 10)
    response.raise_for_status()
    
    # 取得したテキストデータをCSVとして読み込む
    f = StringIO(response.text)
    reader = csv.reader(f)
    
    data_list = []
    for row in reader:
        # 空行やデータが3列ない行はスキップ
        if not row or len(row) < 3:
            continue
            
        # 2列目(row[1])は "2026-08-28T09:06:02Z" の形式なので分割
        datetime_str = row[1].replace('Z', '')
        if 'T' in datetime_str:
            date_part, time_part = datetime_str.split('T')
        else:
            date_part, time_part = datetime_str, ""

        data_list.append({
            "buoy_id": row[0],
            "date": date_part,
            "time": time_part,
            "payload": row[2]
        })
            
    return data_list
