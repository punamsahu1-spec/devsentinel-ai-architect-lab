import unittest

from app.redactor import redact_secrets


class TestRedactor(unittest.TestCase):

    def test_redacts_password_assignment(self):
        text = 'password = "mysecretpassword123"'

        redacted = redact_secrets(text)

        self.assertNotIn("mysecretpassword123", redacted)
        self.assertIn("[REDACTED_PASSWORD_ASSIGN]", redacted)

    def test_redacts_connection_string(self):
        text = 'database_url = "postgresql://admin:adminpass@localhost:5432/appdb"'

        redacted = redact_secrets(text)

        self.assertNotIn("adminpass", redacted)
        self.assertIn("[REDACTED_CONNECTION_STRING]", redacted)

    def test_safe_text_is_unchanged(self):
        text = 'database_url = os.getenv("DATABASE_URL")'

        redacted = redact_secrets(text)

        self.assertEqual(redacted, text)


if __name__ == "__main__":
    unittest.main()