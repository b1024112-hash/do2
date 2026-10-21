import os
from api.scraper import fetch_raw_csv_data
from api.transformer import transform_to_sensor_data

def main():
    # 1. データを取得・変換
    raw_data = fetch_raw_csv_data()
    clean_data = transform_to_sensor_data(raw_data)
    output_text = "\n".join(clean_data)
    
    # 2. GitHub Pages用の公開フォルダ(public)を作成
    os.makedirs("public", exist_ok=True)
    
    # 3. ブラウザで見やすいようにHTMLの <pre> タグで囲んで保存
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>Sensor Data</title></head>\n")
        f.write("<body>\n<pre>\n")
        f.write(output_text)
        f.write("\n</pre>\n</body>\n</html>")
        
    print("Data successfully generated in public/index.html")

if __name__ == "__main__":
    main()
