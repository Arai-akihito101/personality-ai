"""Ollamaに接続せずに基本動作を確認するテスト。"""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock
from urllib.request import Request, urlopen

import ao_web


class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.old = (
            ao_web.HISTORY_FILE, ao_web.MEMORY_FILE, ao_web.SETTINGS_FILE,
            list(ao_web.history), list(ao_web.memories), ao_web.persona,
        )
        ao_web.HISTORY_FILE = Path(self.temp.name) / "history.json"
        ao_web.MEMORY_FILE = Path(self.temp.name) / "memories.json"
        ao_web.SETTINGS_FILE = Path(self.temp.name) / "settings.json"
        ao_web.history.clear()
        ao_web.memories.clear()
        ao_web.persona = "私はアオという日本語AIです。"
        self.server = ao_web.ThreadingHTTPServer(("127.0.0.1", 0), ao_web.App)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        (ao_web.HISTORY_FILE, ao_web.MEMORY_FILE, ao_web.SETTINGS_FILE,
         prev_history, prev_memory, ao_web.persona) = self.old
        ao_web.history[:] = prev_history
        ao_web.memories[:] = prev_memory

    def get(self, path):
        with urlopen("http://127.0.0.1:{}{}".format(self.port, path), timeout=3) as r:
            return r.status, r.read(), r.headers.get("Content-Type", "")

    def post(self, path, payload, origin=None):
        headers = {"Content-Type": "application/json"}
        if origin:
            headers["Origin"] = origin
        req = Request(
            "http://127.0.0.1:{}{}".format(self.port, path),
            data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
        )
        with urlopen(req, timeout=3) as r:
            return json.load(r)

    def test_static_and_initial_state(self):
        status, page, mimetype = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"<!doctype html>", page)
        self.assertIn("text/html", mimetype)
        for path, mime in (("/style.css", "text/css"), ("/app.js", "javascript")):
            status, body, content_type = self.get(path)
            self.assertEqual(status, 200)
            self.assertIn(mime, content_type)
            self.assertGreater(len(body), 100)
        status, raw, _ = self.get("/api/state")
        obj = json.loads(raw)
        self.assertEqual(obj["history"], [])
        self.assertEqual(obj["memories"], [])

    def test_chat_memory_persona_and_delete(self):
        with mock.patch.object(ao_web, "generate_answer", return_value="やあ、よろしく。") as engine:
            self.assertEqual(self.post("/api/chat", {"message": "こんにちは"})["answer"],
                             "やあ、よろしく。")
            engine.assert_called_once_with("こんにちは")
        history = json.loads(ao_web.HISTORY_FILE.read_text(encoding="utf-8"))
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["content"], "こんにちは")
        self.assertEqual(self.post("/api/memory", {"item": "宇宙が好き"})["memories"],
                         ["宇宙が好き"])
        self.assertEqual(self.post("/api/persona", {"persona": "私は真面目なAIです。"})["ok"], True)
        self.assertEqual(ao_web.load_persona(), "私は真面目なAIです。")
        self.assertEqual(self.post("/api/forget", {"index": 0})["memories"], [])
        self.assertTrue(self.post("/api/reset", {})["ok"])
        self.assertEqual(json.loads(ao_web.HISTORY_FILE.read_text(encoding="utf-8")), [])


if __name__ == "__main__":
    unittest.main()
