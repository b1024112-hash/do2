import os
from pathlib import Path
from dotenv import load_dotenv

# settings.py が api/ ディレクトリ内にあると仮定し、1つ上の階層の .env を読み込む
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

# .envファイルからURLを取得
API_URL = os.getenv("DO2_API_URL")

if not API_URL:
    raise RuntimeError("環境変数 'DO2_API_URL' が設定されていません。.envファイルを確認してください。")