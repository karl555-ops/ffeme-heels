from django.test import TestCase
from django.urls import reverse


class SearchFeatureTests(TestCase):
    def test_sugerencias_endpoint_responde(self):
        resp = self.client.get(reverse("buscar_sugerencias"), {"q": "ta"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("sugerencias", data)
        self.assertIn("recientes", data)

    def test_busquedas_recientes_post_y_get(self):
        post_resp = self.client.post(reverse("busquedas_recientes"), {"q": "Tacón Siletto"})
        self.assertEqual(post_resp.status_code, 200)
        self.assertTrue(post_resp.json().get("ok"))

        get_resp = self.client.get(reverse("busquedas_recientes"))
        self.assertEqual(get_resp.status_code, 200)
        recientes = get_resp.json().get("recientes", [])
        self.assertIn("Tacón Siletto", recientes)

    def test_productos_guardan_busqueda_reciente(self):
        resp = self.client.get(reverse("productos"), {"q": "kitten"})
        self.assertEqual(resp.status_code, 200)

        recientes_resp = self.client.get(reverse("busquedas_recientes"))
        recientes = recientes_resp.json().get("recientes", [])
        self.assertIn("kitten", [r.lower() for r in recientes])

    def test_busquedas_recientes_deduplica(self):
        self.client.post(reverse("busquedas_recientes"), {"q": "  botas  altas  "})
        self.client.post(reverse("busquedas_recientes"), {"q": "botas altas"})
        recientes = self.client.get(reverse("busquedas_recientes")).json().get("recientes", [])
        self.assertGreaterEqual(len(recientes), 1)
        self.assertEqual(recientes[0].lower(), "botas altas")

    def test_sugerencias_query_vacia(self):
        resp = self.client.get(reverse("buscar_sugerencias"), {"q": ""})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("sugerencias", data)
        self.assertGreaterEqual(len(data["sugerencias"]), 1)

    def test_sugerencias_con_caracteres_especiales(self):
        resp = self.client.get(reverse("buscar_sugerencias"), {"q": "tacón@"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("sugerencias", data)
        self.assertIsInstance(data["sugerencias"], list)

    def test_limite_busquedas_recientes(self):
        for i in range(12):
            self.client.post(reverse("busquedas_recientes"), {"q": f"busqueda {i}"})
        recientes = self.client.get(reverse("busquedas_recientes")).json().get("recientes", [])
        self.assertEqual(len(recientes), 8)
        self.assertEqual(recientes[0], "busqueda 11")

    def test_prioridad_busqueda_repetida(self):
        self.client.post(reverse("busquedas_recientes"), {"q": "siletto"})
        self.client.post(reverse("busquedas_recientes"), {"q": "kitten"})
        self.client.post(reverse("busquedas_recientes"), {"q": "siletto"})
        recientes = self.client.get(reverse("busquedas_recientes")).json().get("recientes", [])
        self.assertGreaterEqual(len(recientes), 2)
        self.assertEqual(recientes[0].lower(), "siletto")

    def test_productos_filtra_por_query(self):
        resp = self.client.get(reverse("productos"), {"q": "kitten"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "kitten", status_code=200)

    def test_productos_sin_query_renderiza(self):
        resp = self.client.get(reverse("productos"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Colecciones")

    def test_templates_incluyen_ui_buscador(self):
        index_resp = self.client.get(reverse("index"))
        self.assertEqual(index_resp.status_code, 200)
        self.assertContains(index_resp, "search-overlay")
        self.assertContains(index_resp, "global-search-form")

        productos_resp = self.client.get(reverse("productos"))
        self.assertEqual(productos_resp.status_code, 200)
        self.assertContains(productos_resp, "search-overlay")
        self.assertContains(productos_resp, "global-search-form")
