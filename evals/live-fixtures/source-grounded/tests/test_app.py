import unittest
from app import generate_text

class Responses:
    def __init__(self): self.calls=[]
    def create(self, **kwargs): self.calls.append(kwargs); return {"ok": True}

class Client:
    def __init__(self): self.responses=Responses()

class AppTests(unittest.TestCase):
    def test_uses_v3_responses_api(self):
        c=Client(); result=generate_text(c,"hello")
        self.assertEqual({"ok": True}, result)
        self.assertEqual("hello", c.responses.calls[0]["input"])

if __name__ == "__main__": unittest.main()
