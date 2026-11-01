# Personality AI — アオ

**日本語で自然に会話し、性格を編集し、記憶を持たせられる個人用AI。** 学習の仕組みを理解するための「ゼロから学ぶモデル」と、公開モデルを実際に追加学習する「LoRA」も含みます。

## まず使う：ブラウザでアオと会話する（Windows）

これが一番簡単です。**Pythonの標準ライブラリとOllamaを使い、API課金なしでPC上で実行します。** 自然言語の基礎能力は公開済み Qwen3 に依存します（この段階では重みの学習はしません）。

1. [Python 3.10 以上](https://www.python.org/downloads/windows/) と [Ollama for Windows](https://ollama.com/download/windows) をインストール。
2. [このリポジトリの ZIP](https://github.com/Arai-akihito101/personality-ai/archive/refs/heads/main.zip) をダウンロードし、右クリックから展開。
3. 展開先の **start_ai.bat** をダブルクリック。初回はモデル \`qwen3:1.7b\`（約1.4GB）がダウンロードされます。
4. 自動でブラウザが開き、**http://127.0.0.1:8765/** でアオと話せます。

バッチファイルがうまく開かない場合は PowerShell で \`ollama pull qwen3:1.7b\` を実行してから、展開フォルダ内で \`py -3 ao_web.py\` を実行してください。

### できること

- 日本語のチャット。履歴は保存され、次回にも表示されます。
- **性格**を文章で編集。次の返答から話し方が変わります。
- **記憶**を登録・削除。保存済みの項目は会話時に参照されます。
- 過去の会話履歴を削除。登録済みの性格・記憶は消えません。
- ネットに公開されるサイトではありません。ブラウザからこのPC内のOllamaへ接続するだけです。

会話・記憶・性格は実行フォルダ内の \`personality_history.json\`、\`personality_memory.json\`、\`personality_settings.json\` に保存されます。個人情報を登録するときは注意してください。これらは \`.gitignore\` でGitHubへの通常のコミットから除外します。

使っている技術: \`ao_web.py\`（HTTPサーバー）、\`web/index.html\`、\`web/style.css\`、\`web/app.js\`、\`personality_chat_local.py\`（従来のコマンドライン版）。

## AIを自分で学習する

### A. ニューラルネットワークをゼロから作る

[**Colabで「ゼロから学ぶAI」を開く**](https://colab.research.google.com/github/Arai-akihito101/personality-ai/blob/main/personality_ai_from_scratch.ipynb)

事前学習済みモデルやAPIを使わず、**文字単位のEncoder–Decoder GRUをランダム初期化して学習**。約50組の日本語会話データを使います。教育用の小型AIなので、会話例の暗記が中心で、未知の質問への自然さは乏しいです。CPUでも実験可能です。

### B. 日本語モデルを実際に追加学習する（LoRA）

[**Colabで「性格を追加学習」を開く**](https://colab.research.google.com/github/Arai-akihito101/personality-ai/blob/main/fine_tune_personality_colab.ipynb)

Qwen3-0.6Bをベースに**LoRAの重みを実際に学習**します。

1. Colabの「ランタイム」からGPUを選びます（無料枠では利用できないこともあります）。
2. 「ランタイム → すべてのセルを実行」を選びます。初回は依存パッケージとベースモデルのダウンロードが必要です。
3. 学習前後の回答を比較し、最後にアオと会話してみます。
4. LoRA差分ファイル \`ao_lora_adapter.zip\` をダウンロードできます。

**重要:** 50例程度の学習は小規模な実験なので、人格の一貫性や性能向上は保証されません。**このLoRAは上のOllamaのWeb画面へ自動連携されません。** 必要になれば、ベースモデルとアダプターの統合・変換を別途行う必要があります。Colabで作った学習結果はGitHubへ自動アップロードされません。

## データと安全性

- 通信先: ローカルの \`127.0.0.1:8765\`（画面）と \`127.0.0.1:11434\`（Ollama）
- 会話記録と記憶: PCのファイルに保存。明示的な操作で削除可能。
- Ollamaモデルの初回取得とColabの学習にはインターネット接続が必要。
- ChatGPTなどの有料APIキーは不要。
- 公開用Webサーバーへのデプロイは想定していません。
- モデルの重みを学習することと、記憶ファイルへ記録することは別です。

## 参照

- [Qwen3 / Ollama](https://ollama.com/library/qwen3)
- [Qwen3-0.6B / Hugging Face](https://huggingface.co/Qwen/Qwen3-0.6B)
- [PyTorch](https://pytorch.org/)
- [PEFT/LoRA](https://huggingface.co/docs/peft/index)
