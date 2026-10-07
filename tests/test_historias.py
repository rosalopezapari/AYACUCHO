import unittest

from ayacucho.historias import HISTORIAS


class TestHistorias(unittest.TestCase):
    def test_lista_no_vacia(self):
        self.assertTrue(HISTORIAS)

    def test_estructura(self):
        for h in HISTORIAS:
            self.assertIn("titulo", h)
            self.assertIn("contenido", h)
            self.assertTrue(h["contenido"])

    def test_titulos_clave_estan_presentes(self):
        titulos = " ".join(h["titulo"] for h in HISTORIAS).lower()
        self.assertIn("batalla de ayacucho", titulos)
        self.assertIn("huamanga", titulos)


if __name__ == "__main__":
    unittest.main()