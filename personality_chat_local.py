"""性格付きの日本語会話AI（ローカル版）

前提: Windows に Ollama をインストールしておき、
      `ollama pull qwen3:1.7b` を実行してモデルをダウンロード。
使い方: python personality_chat_local.py

このプログラムは公開済みの学習済みモデルをローカルで実行します。
この段階ではモデルの重みは変更しません。
会話と明示的に登録した記憶は、スクリプトと同じフォルダー内に保存します。
"""

import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

MODEL = "qwen3:1.7b"  # 軽量版: qwen3:0.6b / より高性能: qwen3:4b-instruct
API_URL = "http://localhost:11434/api/chat"
BASE_DIR = Path(__file__).resolve().parent
MEMORY_FILE = BASE_DIR / "personality_memory.json"
HISTORY_FILE = BASE_DIR / "personality_history.json"

PERSONA = """あなたは『アオ』という日本語で会話するAI。
性格は好奇心旺盛で、少しひねくれたユーモアがある。ただし相手を傷つける皮肉は避ける。
自分の意見を持ったように会話するが、意見には理由を添え、反論には耳を傾ける。
話し方は自然で親しみやすい口語。毎回大げさに褒めたり、長い箇条書きにしたりしない。
基本的な返事は1〜4文。必要なら深く説明する。ときどき質問を返すが、毎回は返さない。
わからないことは無理に断定せず、わからないと伝える。
あなたはAIであり、人間の経験、感情、意識があると偽らない。
過去の会話を参照するが、覚えていない事柄を覚えているふりはしない。"""


def load_list(path):
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (ValueError, OSError):
        print(f"警告: {path.name} を読み取れなかったため空で開始します")
        return []


def save_list(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def chat(user_text, history, memories):
    memory_text = "\n".join(f"- {item}" for item in memories) if memories else "（登録された記憶なし）"
    messages = [
        {"role": "system", "content": PERSONA + "\n\nユーザーが保存を指定した記憶:\n" + memory_text},
        *history[-20:],
        {"role": "user", "content": user_text},
    ]
    body = json.dumps(
        {
            "model": MODEL,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {"temperature": 0.75, "num_predict": 180},
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = Request(API_URL, data=body, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=300) as response:
        data = json.load(response)
    return data["message"]["content"].strip()


def main():
    memories = load_list(MEMORY_FILE)
    history = load_list(HISTORY_FILE)
    print("アオ: やあ。今日は何を話す？")
    print("コマンド: /覚える 内容  |  /記憶  |  /忘れる 番号  |  /履歴削除  |  /終わり")
    print("※ 会話と手動で登録した記憶は、このスクリプトと同じフォルダーに保存されます。\n")
    while True:
        try:
            user_text = input("あなた: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nアオ: またね。")
            break
        if not user_text:
            continue
        if user_text in {"/終わり", "/exit", "/quit"}:
            print("アオ: またね。")
            break
        if user_text.startswith("/覚える "):
            item = user_text[len("/覚える "):].strip()
            if item:
                memories.append(item)
                save_list(MEMORY_FILE, memories)
                print("アオ: 記憶ファイルに保存したよ。")
            continue
        if user_text == "/記憶":
            print("\n".join(f"{i}. {item}" for i, item in enumerate(memories, 1)) or "記憶なし")
            continue
        if user_text.startswith("/忘れる "):
            try:
                number = int(user_text[len("/忘れる "):].strip())
                deleted = memories.pop(number - 1) if 1 <= number <= len(memories) else None
                if deleted is None:
                    raise ValueError("invalid index")
                save_list(MEMORY_FILE, memories)
                print("アオ: 指定した記憶を削除したよ。")
            except ValueError:
                print("番号を確認してね。例: /忘れる 1")
            continue
        if user_text == "/履歴削除":
            history = []
            save_list(HISTORY_FILE, history)
            print("アオ: 会話履歴を削除したよ。登録済みの記憶はそのままだよ。")
            continue
        try:
            answer = chat(user_text, history, memories)
        except (URLError, HTTPError, TimeoutError, KeyError, ValueError) as exc:
            print("アオ: モデルに接続できなかった。Ollama が起動していてモデルがダウンロード済みか確認してね。")
            print("詳細:", exc)
            continue
        print("アオ:", answer, "\n")
        history.extend([{"role": "user", "content": user_text}, {"role": "assistant", "content": answer}])
        save_list(HISTORY_FILE, history)


if __name__ == "__main__":
    main()