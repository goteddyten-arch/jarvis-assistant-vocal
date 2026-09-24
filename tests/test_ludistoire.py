import json
import os
import unittest
from unittest.mock import MagicMock, patch

from core import registre
from tools import ludistoire


class _Reponse:
    def __init__(self, contenu: bytes):
        self.contenu = contenu
        self.headers = {"Content-Length": str(len(contenu))}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, _taille):
        return self.contenu


class LudistoireTests(unittest.TestCase):
    def test_outil_est_n1_local_et_lecture_seule(self):
        outil = registre.get("ludistoire_status")
        self.assertIsNotNone(outil)
        self.assertEqual(registre.niveau("ludistoire_status"), "N1")
        self.assertFalse(outil.mcp_expose)

    @patch.dict(os.environ, {
        "JARVIS_LUDISTOIRE_STATUS_URL": "https://preprod.ludistoire.fr/api/jarvis/status",
        "JARVIS_LUDISTOIRE_TOKEN": "secret-test",
    }, clear=False)
    @patch("tools.ludistoire.urlopen")
    def test_statut_appelle_api_en_get_avec_bearer(self, ouvrir):
        ouvrir.return_value = _Reponse(b'{"deployment":"ok","factory":"idle"}')

        resultat = json.loads(ludistoire.ludistoire_status())

        self.assertEqual(resultat["deployment"], "ok")
        requete = ouvrir.call_args.args[0]
        self.assertEqual(requete.get_method(), "GET")
        self.assertEqual(requete.get_header("Authorization"), "Bearer secret-test")

    @patch.dict(os.environ, {
        "JARVIS_LUDISTOIRE_STATUS_URL": "http://example.com/status",
    }, clear=False)
    def test_http_distant_est_refuse(self):
        resultat = ludistoire.ludistoire_status()
        self.assertIn("HTTPS", resultat)

    @patch.dict(os.environ, {}, clear=True)
    def test_configuration_manquante_est_expliquee(self):
        resultat = ludistoire.ludistoire_status()
        self.assertIn("JARVIS_LUDISTOIRE_STATUS_URL", resultat)


if __name__ == "__main__":
    unittest.main()
