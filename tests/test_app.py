import unittest

from app import app


class HomeRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_renders_the_portfolio_page(self):
        response = self.client.get("/")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Yashpal", page)
        self.assertIn("Cloud &amp; DevOps Engineer", page)
        self.assertIn("/static/style.css", page)

    def test_stylesheet_is_available(self):
        response = self.client.get("/static/style.css")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/css", response.content_type)
        response.close()


if __name__ == "__main__":
    unittest.main()