# DO2 API 

DO2センサ用の FastAPI バックエンド API です。

---

## 🛠 前提条件

いずれかの環境が必要です：
- **Docker 環境で動かす場合 (推奨)**: [Docker Desktop](https://www.docker.com/products/docker-desktop/) が起動していること
- **ローカル Python 環境で動かす場合**: Python 3.11 以上 (または [uv](https://docs.astral.sh/uv/))

---

## 🚀 起動方法

### 方法 1: Docker Compose を使用する場合 (推奨)

最も簡単に環境を構築・起動できます。

1. **Docker Desktop を起動** しておきます。
2. 以下のコマンドを実行してビルド＆コンテナ起動：

```bash
docker compose up --build
```

- コンテナ停止: ターミナルで `Ctrl + C`（または別ターミナルで `docker compose down`）

---

### 方法 2: ローカル Python 環境で起動する場合

#### `uv` を使用する場合:
```bash
uv run uvicorn api.index:app --reload --port 8000
```

#### `pip` / `venv` を使用する場合:
```bash
# 仮想環境作成＆有効化
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 依存パッケージインストール
pip install -r requirements.txt

# サーバー起動
uvicorn api.index:app --reload --port 8000
```

---

## 📖 API の確認・ドキュメント

サーバー起動後、ブラウザで以下にアクセスしてください：

- **トップページ**: [http://localhost:8000/](http://localhost:8000/)
- **対話型 API ドキュメント (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **代替 API ドキュメント (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🌐 Render へのデプロイ

[Render](https://render.com/) の Web Service としてデプロイ可能です。

- **Runtime / Environment**: `Docker`
- GitHub リポジトリを連携して `main` ブランチを指定するだけで、自動で Dockerfile を読み込んでビルド・起動されます。

---

## 📁 ディレクトリ構成

```text
DO2_API/
├── api/
│   └── index.py            # FastAPI アプリケーションコード
├── Dockerfile              # コンテナビルド設定
├── docker-compose.yml      # コンテナ一括起動設定
├── .dockerignore           # Docker 除外設定
├── requirements.txt        # 依存パッケージリスト
├── pyproject.toml          # プロジェクト・uv設定
└── README.md               # 本ドキュメント
```
