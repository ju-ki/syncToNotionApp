# 🧩 GitHub Issues to Notion Sync

GitHub の Issue を Notion データベースと同期する Python スクリプトです。  
GitHub Actions を使って、Issue が作成・更新・クローズされたときに Notion に自動で反映されます。

---

## 📦 機能

- Open 状態の GitHub Issue を Notion に同期
- 初回移行時には Notion データベースが空であれば一括登録（Bulk Insert）
- 既に存在する Issue は自動で更新
- Pull Request は無視されます

---

## 📁 ディレクトリ構成

```plaintext
your-project/
├── .github/
│   └── workflows/
│       └── sync-github-to-notion.yml  ← GitHub Actions の設定ファイル
├── tools/
│   ├── app.py
│   ├── requirements.txt
│   └── .env.example
```

---

## 🚀 導入手順

### 1. ファイルを設置

既存プロジェクトの中に `tools/` フォルダを作成し、スクリプト一式を配置します。  
GitHub Actions の `.yml` ファイルは `.github/workflows/sync-github-to-notion.yml` に配置します。

---

### 2. 環境変数を登録（GitHub Secrets）

以下の環境変数を GitHub のリポジトリ設定 → **Settings > Secrets and variables > Actions > Secrets** に登録してください。

| Key                    | 用途                            |
|------------------------|---------------------------------|
| `NOTION_API_KEY`       | Notion の統合トークン           |
| `NOTION_DATABASE_ID`   | 対象となる Notion データベース ID |
| `PROJECT_ID`           | Notion のプロジェクトページ ID（Relation 用） |
| `PERSONAL_GITHUB_TOKEN`| GitHub の個人アクセストークン（`repo` スコープが必要） |

---

### 3. `.env.example` を参考に `.env` を作成（ローカル実行時）

```env
NOTION_API_KEY=your_notion_secret
NOTION_DATABASE_ID=your_database_id
PROJECT_ID=your_project_relation_id
GITHUB_TOKEN=your_personal_github_token
GITHUB_REPO=user/repo
```

`.env` ファイルは `.gitignore` に追加して、リポジトリに含めないようにしてください。
### 4. 必要なライブラリをインストール
```bash
pip install -r tools/requirements.txt
```
### 5. GitHub Actions を有効化

特別な設定は不要です。ワークフローは GitHub Issue の作成・編集・クローズ時に自動で実行されます。

---

## 🧪 ローカルでの動作確認

以下のコマンドで、open 状態の Issue を手動で同期できます。

```bash
python tools/app.py
