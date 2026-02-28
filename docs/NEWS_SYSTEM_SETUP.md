# ラグビーニュース自動生成システム セットアップガイド

## 📋 必要なもの

1. **Gemini API Key** (無料)
2. **Python パッケージ**

---

## 🔑 Step 1: Gemini API Keyの取得

1. https://makersuite.google.com/app/apikey にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリック
4. API Keyをコピー

---

## 📦 Step 2: 依存パッケージのインストール

### オプション A: 仮想環境を使用（推奨）

```bash
cd /Users/ktamatzmoto/Desktop/rugbypicks

# 仮想環境作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# パッケージインストール
pip install google-generativeai pillow beautifulsoup4 requests

# 使用後は無効化
# deactivate
```

### オプション B: システムワイドインストール

```bash
pip3 install --break-system-packages google-generativeai pillow beautifulsoup4 requests
```

---

## 🔧 Step 3: API Keyの設定

### 方法1: 環境変数（推奨）

```bash
export GEMINI_API_KEY='AIzaSyCA5Ke0DXp5Q15oJ44fD1BdLsjluRIv7d0'
```

永続化する場合は `~/.zshrc` または `~/.bash_profile` に追加：

```bash
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 方法2: スクリプト内に直接記載

`generate_rugby_articles.py` の最初の方で：

```python
generator = RugbyArticleGenerator(api_key='your-api-key-here')
```

---

## 🚀 使い方

### 1. ニュースをスクレイピング

```bash
python3 scrape_rugby_news.py
```

出力: `scraped_news.json`

### 2. 記事を生成

```bash
python3 generate_rugby_articles.py
```

出力: `news_article_1_transfer.txt`, `news_article_2_callup.txt`, etc.

### 3. サムネイル生成

```bash
python3 generate_thumbnails.py
```

出力: `news/thumbnails/*.png`

---

## 📝 テスト実行

全てセットアップできたら、以下のコマンドで5記事生成：

```bash
# 1. ニューススクレイピング
python3 scrape_rugby_news.py

# 2. 記事生成（5記事）
python3 generate_rugby_articles.py

# 3. サムネイル生成
python3 generate_thumbnails.py
```

---

## ⚠️ トラブルシューティング

### エラー: "GEMINI_API_KEY not set"
→ Step 3を確認。環境変数が設定されているか確認：
```bash
echo $GEMINI_API_KEY
```

### エラー: "externally-managed-environment"
→ 仮想環境を使用（オプションA）

### エラー: "No module named 'google.generativeai'"
→ パッケージが未インストール。Step 2を再実行

---

## 📊 無料枠の制限

Gemini API 無料枠:
- **15 requests/minute**
- **1,500 requests/day**

→ 1日5〜10記事なら十分

---

## 次のステップ

セットアップ完了後：
1. テスト記事（5記事）を生成
2. 品質確認
3. HTML生成スクリプト作成
4. 自動投稿システム構築
