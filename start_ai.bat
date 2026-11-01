@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===============================
echo  アオ - 日本語会話AI
echo ===============================
where py >nul 2>nul
if errorlevel 1 (
  echo Python が見つかりません。Python 3 をインストールしてください。
  pause
  exit /b 1
)
where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama が見つかりません。https://ollama.com/download/windows からインストールしてください。
  pause
  exit /b 1
)
ollama list | findstr /c:"qwen3:1.7b" >nul
if errorlevel 1 (
  echo 初回は AI モデルをダウンロードします。
  ollama pull qwen3:1.7b
  if errorlevel 1 (
    echo モデルを準備できませんでした。Ollama を起動して再試行してください。
    pause
    exit /b 1
  )
)
echo ブラウザが開きます。終了は Ctrl+C です。
py -3 ao_web.py
pause
