import unittest
from utils.processor import extract_first_name, extract_name_from_email, get_first_name, personalize_template

class TestProcessor(unittest.TestCase):
    def test_extract_first_name(self):
        self.assertEqual(extract_first_name("Rahul Sharma"), "Rahul")
        self.assertEqual(extract_first_name("John F. Kennedy"), "John")
        self.assertEqual(extract_first_name("Alice"), "Alice")
        self.assertIsNone(extract_first_name(""))
        self.assertIsNone(extract_first_name(None))

    def test_extract_name_from_email(self):
        self.assertEqual(extract_name_from_email("john.doe@company.com"), "John")
        self.assertEqual(extract_name_from_email("sarah_connor@tech.io"), "Sarah")
        self.assertEqual(extract_name_from_email("alexander-smith@domain.org"), "Alexander")
        self.assertIsNone(extract_name_from_email("info@company.com"))
        self.assertIsNone(extract_name_from_email("contact@domain.com"))
        self.assertIsNone(extract_name_from_email("careers@firm.org"))

    def test_get_first_name_fallback(self):
        # Direct full name available
        self.assertEqual(get_first_name({"full_name": "David Miller", "email": "dave@example.com"}), "David")
        # Full name missing, fall back to email
        self.assertEqual(get_first_name({"full_name": "", "email": "emily.watson@example.com"}), "Emily")
        # Neither available, fall back to default
        self.assertEqual(get_first_name({"full_name": "", "email": "support@example.com"}), "there")

    def test_personalize_template(self):
        template = "Hi {first_name}, I saw your role at {company}."
        row = {"full_name": "Bruce Wayne", "company": "Wayne Enterprises"}
        result = personalize_template(template, row)
        self.assertEqual(result, "Hi Bruce, I saw your role at Wayne Enterprises.")

if __name__ == "__main__":
    unittest.main()
