# Personality AI — 性格のある日本語AIを育てる

自分だけの性格・会話スタイルを持つ日本語AIをつくるための学習用リポジトリです。

## 1. ニューラルネットワークをゼロから学ぶ

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Arai-akihito101/personality-ai/blob/main/personality_ai_from_scratch.ipynb)

[Colab でノートブックを開く](https://colab.research.google.com/github/Arai-akihito101/personality-ai/blob/main/personality_ai_from_scratch.ipynb)

`personality_ai_from_scratch.ipynb` は、PyTorch で GRU の Encoder–Decoder をランダム初期化し、少量の日本語会話例から学習します。コードをColabで開いたら、上から順番にセルを実行します。

**注意：** 教材用の小さなモデルです。会話例の記憶に近く、未知の質問への一般化は限定的です。ChatGPTのような自然な対話は期待できません。

## 2. 自然な会話を試す（ローカル PC）

`personality_chat_local.py` は、Ollama 上の学習済みモデルを利用した日本語会話プログラムです。こちらはモデルをゼロから訓練するものではありません。

1. [Ollama](https://ollama.com/download/windows) をインストール
2. PowerShell で `ollama pull qwen3:1.7b` を実行
3. このリポジトリからスクリプトを取得し、`py personality_chat_local.py` で起動

会話ログ・記憶ファイルには個人情報が含まれ得ます。GitHub にコミットしないでください。

## 今後の予定

- 会話データを増やして学習を比較する
- 性格や発話スタイルの評価指標を加える
- LoRA による公開モデルの追加学習に挑戦する
