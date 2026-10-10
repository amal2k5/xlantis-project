from django.conf import settings
from django.test import SimpleTestCase


class ProjectConfigurationTests(SimpleTestCase):
    def test_health_check_endpoint(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("service", data)

    def test_database_engine_is_postgresql(self):
        engine = settings.DATABASES["default"]["ENGINE"]
        self.assertIn(
            "postgresql",
            engine,
            f"Expected PostgreSQL backend engine, got '{engine}'",
        )

    def test_installed_apps_configured(self):
        self.assertIn("rest_framework", settings.INSTALLED_APPS)
        self.assertIn("apps.directory.apps.DirectoryConfig", settings.INSTALLED_APPS)
        self.assertIn("apps.platforms.apps.PlatformsConfig", settings.INSTALLED_APPS)
