"""Pont local, minimal et en lecture seule vers Ludistoire.

Le connecteur ne connait ni MySQL ni D1 : il appelle uniquement une URL HTTPS
explicitement configuree. Les futures actions d'ecriture resteront dans des
outils separes, avec confirmation et garde-fous adaptes.
"""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from core.registre import outil

_TIMEOUT_SECONDES = 8
_TAILLE_MAX = 256 * 1024


def _url_statut() -> str:
    url = os.environ.get("JARVIS_LUDISTOIRE_STATUS_URL", "").strip()
    if not url:
        raise ValueError(
            "Configure JARVIS_LUDISTOIRE_STATUS_URL avec l'endpoint de statut."
        )
    parsed = urlparse(url)
    local = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    if parsed.scheme != "https" and not (parsed.scheme == "http" and local):
        raise ValueError("L'URL Ludistoire doit utiliser HTTPS (HTTP permis en local).")
    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("L'URL Ludistoire configuree n'est pas valide.")
    return url


def _lire_statut() -> dict:
    entetes = {"Accept": "application/json", "User-Agent": "Jarvis-Ludistoire/1"}
    jeton = os.environ.get("JARVIS_LUDISTOIRE_TOKEN", "").strip()
    if jeton:
        entetes["Authorization"] = f"Bearer {jeton}"

    requete = Request(_url_statut(), headers=entetes, method="GET")
    with urlopen(requete, timeout=_TIMEOUT_SECONDES) as reponse:
        taille = reponse.headers.get("Content-Length")
        if taille and int(taille) > _TAILLE_MAX:
            raise ValueError("La reponse Ludistoire est trop volumineuse.")
        contenu = reponse.read(_TAILLE_MAX + 1)
        if len(contenu) > _TAILLE_MAX:
            raise ValueError("La reponse Ludistoire est trop volumineuse.")
        donnees = json.loads(contenu.decode("utf-8"))
        if not isinstance(donnees, dict):
            raise ValueError("Ludistoire n'a pas renvoye un objet JSON.")
        return donnees


@outil(
    nom="ludistoire_status",
    description=(
        "Lit l'etat de Ludistoire et de la Factory via leur API dediee, sans acces "
        "direct a MySQL ou D1 et sans aucune ecriture. A utiliser pour demander si "
        "Ludistoire fonctionne, l'etat du catalogue, de la Factory ou du deploiement."
    ),
    lent=True,
    phrase_attente="Je verifie Ludistoire.",
    mcp_expose=False,
    affichage="toujours",
)
def ludistoire_status() -> str:
    try:
        statut = _lire_statut()
    except HTTPError as exc:
        if exc.code in {401, 403}:
            return "Ludistoire repond, mais l'acces Jarvis est refuse. Verifie le jeton de lecture."
        return f"Ludistoire repond avec une erreur HTTP {exc.code}."
    except (URLError, TimeoutError):
        return "Ludistoire est injoignable pour le moment."
    except (ValueError, json.JSONDecodeError) as exc:
        return f"Configuration ou reponse Ludistoire invalide : {exc}"

    # JSON compact : le LLM peut ensuite produire une reponse naturelle et ciblee.
    return json.dumps(statut, ensure_ascii=False, separators=(",", ":"))
