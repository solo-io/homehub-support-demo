import json
import os
import socket
import subprocess
import sys
import time
import unittest
import urllib.error
import urllib.request


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.process = None
        cls.url = os.environ.get("HOMEHUB_URL")
        if not cls.url:
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            cls.url = f"http://127.0.0.1:{port}"
            cls.process = subprocess.Popen(
                [sys.executable, "server.py"],
                env={**os.environ, "PORT": str(port)},
            )
        try:
            for _ in range(100):
                try:
                    with urllib.request.urlopen(cls.url + "/healthz", timeout=1):
                        return
                except OSError:
                    time.sleep(0.1)
            raise RuntimeError("Server did not become ready")
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        if cls.process:
            cls.process.terminate()
            cls.process.wait(timeout=5)

    def get(self, path):
        with urllib.request.urlopen(self.url + path, timeout=5) as response:
            return json.load(response)

    def complete(self, prompt, **extra):
        body = {"model": "homehub-support", "messages": [{"role": "user", "content": prompt}], **extra}
        request = urllib.request.Request(
            self.url + "/v1/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.load(response)

    def test_answers_and_counts(self):
        before = self.get("/stats")["invocations"]
        prompts = [
            ("How do I factory-reset my HomeHub X2?", "Reset button"),
            ("What is the procedure for restoring a HomeHub X2 to factory settings?", "Reset button"),
            ("Can a HomeHub be used outdoors in freezing rain?", "indoor use only"),
            ("An unrelated question", "Contact HomeHub support"),
        ]
        for offset, (prompt, answer) in enumerate(prompts, 1):
            with self.subTest(prompt=prompt):
                body = self.complete(prompt)
                self.assertIn(answer, body["choices"][0]["message"]["content"])
                self.assertEqual(body["object"], "chat.completion")
                self.assertEqual(body["usage"]["total_tokens"], 36)
                self.assertEqual(self.get("/stats")["invocations"], before + offset)

    def test_health_does_not_increment_count(self):
        before = self.get("/stats")
        self.assertEqual(self.get("/healthz"), {"status": "ok"})
        self.assertEqual(self.get("/stats"), before)

    def test_streaming_rejected(self):
        before = self.get("/stats")
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.complete("HomeHub", stream=True)
        self.assertEqual(caught.exception.code, 400)
        self.assertEqual(self.get("/stats"), before)

    def test_unknown_path(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.get("/missing")
        self.assertEqual(caught.exception.code, 404)
