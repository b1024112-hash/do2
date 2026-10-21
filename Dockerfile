FROM python:3.12-slim

WORKDIR /app

# 依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# Renderが環境変数 $PORT でポートを渡してくるため、それをバインドして起動
# （ローカルテスト用にデフォルト8000を設定）
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8000}"]
