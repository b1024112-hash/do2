import requests
import csv
from io import StringIO

# 作成した settings.py から API_URL をインポートする
from .settings import API_URL

def fetch_raw_csv_data() -> list[dict]:
    """URLからCSVテキストを取得し、辞書のリストとして抽出する"""
    
    # 1. 偽装用のヘッダー情報を定義する
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # 2. 修正したコード（ヘッダーとタイムアウト10秒を指定）に置き換える
        response = requests.get(API_URL, headers=headers, timeout=10)
        
        # エラー（404など）が返ってきた場合に例外を発生させる
        response.raise_for_status() 

    except requests.exceptions.RequestException as e:
        # エラーが起きたことをブラウザで確認できるように、ダミーの辞書を返す
        error_msg = f"API_ERROR: {str(e)}"
        print(error_msg)
        return [{
            "buoy_id": "ERROR",
            "date": "1970-01-01",
            "time": "00:00:00",
            "payload": error_msg.encode('utf-8').hex() # エラーメッセージをhexに変換して強引に表示させる
        }]
    
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
