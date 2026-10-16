import unittest
from main import parse_template
from utils.anti_spam import get_daily_limit

class TestConfigAndParser(unittest.TestCase):
    def test_parse_template_with_subject(self):
        content = "Subject: Hello World\n\nThis is the body content."
        subject, body = parse_template(content)
        self.assertEqual(subject, "Hello World")
        self.assertEqual(body, "This is the body content.")

    def test_parse_template_without_subject(self):
        content = "This is a body without subject line."
        subject, body = parse_template(content)
        self.assertEqual(subject, "Connecting regarding opportunities")
        self.assertEqual(body, "This is a body without subject line.")

    def test_get_daily_limit_schedule(self):
        # Days 1-3
        self.assertGreaterEqual(get_daily_limit(1), 25)
        # Days 4-7
        self.assertGreaterEqual(get_daily_limit(5), 25)

if __name__ == "__main__":
    unittest.main()
