from __future__ import annotations

import unittest

from week13.src.app import create_app


class Week13AppTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app()
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_home_exposes_week13_links(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["developer_portal"], "/portal")
        self.assertEqual(payload["swagger_docs"], "/apidocs/")
        self.assertEqual(payload["openapi_json"], "/apispec_1.json")
        self.assertEqual(payload["business_model_canvas"], "/api/business-model")
        self.assertEqual(payload["kpis"], "/api/metrics")

    def test_portal_contains_api_product_sections(self) -> None:
        response = self.client.get("/portal")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("API as a Product", html)
        self.assertIn("Launch Strategy", html)
        self.assertIn("Monetization Model", html)
        self.assertIn("Business Model Canvas", html)
        self.assertIn("Swagger docs", html)
        self.assertIn("registered developers", html)

    def test_swagger_spec_documents_week13_endpoints(self) -> None:
        response = self.client.get("/apispec_1.json")

        self.assertEqual(response.status_code, 200)
        spec = response.get_json()
        self.assertEqual(spec["info"]["title"], "Week13 API as a Product")
        self.assertIn("/api/business-model", spec["paths"])
        self.assertIn("/api/pricing", spec["paths"])
        self.assertIn("/api/metrics", spec["paths"])
        self.assertIn("/api/sandbox", spec["paths"])
        self.assertIn("SandboxBearer", spec["components"]["securitySchemes"])

    def test_business_model_canvas_has_required_blocks(self) -> None:
        response = self.client.get("/api/business-model")

        self.assertEqual(response.status_code, 200)
        canvas = response.get_json()["canvas"]
        self.assertIn("customer_segments", canvas)
        self.assertIn("value_propositions", canvas)
        self.assertIn("revenue_streams", canvas)
        self.assertIn("cost_structure", canvas)

    def test_metrics_include_core_kpis(self) -> None:
        response = self.client.get("/api/metrics")

        self.assertEqual(response.status_code, 200)
        kpis = response.get_json()["kpis"]
        self.assertIn("registered_developers", kpis)
        self.assertIn("call_volume_30d", kpis)
        self.assertIn("error_rate_30d", kpis)
        self.assertLess(kpis["error_rate_30d"], 1)

    def test_pricing_supports_freemium_and_paid_model(self) -> None:
        response = self.client.get("/api/pricing")

        self.assertEqual(response.status_code, 200)
        plans = response.get_json()["plans"]
        names = {plan["name"] for plan in plans}
        self.assertIn("Free", names)
        self.assertIn("Growth", names)
        self.assertTrue(any("call" in plan["price"].lower() for plan in plans))


if __name__ == "__main__":
    unittest.main()
