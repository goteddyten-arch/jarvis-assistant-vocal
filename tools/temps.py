"""Heure/date et minuteur."""
import re
import threading
from datetime import datetime

from core import voix
from core.registre import outil
from core.util import sans_accents


def router_commande_temps(phrase, piece=""):
    """Route localement les demandes temporelles évidentes, sans appeler le LLM.

    Couvre le 80/20 vocal : heure/date et minuteurs simples en chiffres.
    Les formulations ambiguës restent confiées au modèle général.
    """
    p = " ".join(re.sub(
        r"[^a-z0-9]+", " ", sans_accents(str(phrase or "").lower())
    ).split())
    if not p:
        return None

    demandes_heure_date = (
        "quelle heure", "quel heure", "il est quelle heure", "donne moi l heure",
        "donne l heure", "quelle date", "quel jour", "on est quel jour",
        "date aujourd hui", "date d aujourd hui",
    )
    if any(expr in p for expr in demandes_heure_date):
        return "heure_et_date", {}

    m = re.search(
        r"(?:minuteur|chrono(?:metre)?)"
        r"(?:\s+de|\s+pour)?\s+(\d+)\s*"
        r"(seconde|secondes|sec|minute|minutes|min|heure|heures|h)\b",
        p,
    )
    if not m:
        m = re.search(
            r"(?:mets|met|lance|demarre)\s+(?:moi\s+)?(?:un\s+)?minuteur"
            r"(?:\s+de|\s+pour)?\s+(\d+)\s*"
            r"(seconde|secondes|sec|minute|minutes|min|heure|heures|h)\b",
            p,
        )
    if m:
        valeur = int(m.group(1))
        unite = m.group(2)
        facteur = 1 if unite.startswith("sec") else 60 if unite.startswith("min") else 3600
        return "lancer_minuteur", {"secondes": valeur * facteur}

    return None


@outil(
    nom="heure_et_date",
    mcp_expose=True,
    description="Donne l'heure et la date actuelles",
)
def heure_et_date() -> str:
    """Donne l'heure et la date actuelles."""
    maintenant = datetime.now()
    jours = ["lundi", "mardi", "mercredi", "jeudi",
             "vendredi", "samedi", "dimanche"]
    mois = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet",
            "aout", "septembre", "octobre", "novembre", "decembre"]
    return (
        f"Il est {maintenant.hour} heures {maintenant.minute}, "
        f"le {jours[maintenant.weekday()]} {maintenant.day} "
        f"{mois[maintenant.month - 1]} {maintenant.year}."
    )


@outil(
    nom="lancer_minuteur",
    mcp_expose=True,
    description="Lance un minuteur qui previendra a voix haute",
    parametres={
        "type": "object",
        "properties": {
            "secondes": {"type": "integer", "description": "Duree en secondes"},
            "libelle": {"type": "string", "description": "Nom du minuteur"},
        },
        "required": ["secondes"],
    },
)
def lancer_minuteur(secondes: int, libelle: str = "") -> str:
    """Lance un minuteur qui previent a voix haute."""
    secondes = max(1, int(secondes))

    def sonner():
        texte = f"Le minuteur {libelle} est termine." if libelle \
            else "Le minuteur est termine."
        voix.parler(texte)

    threading.Timer(secondes, sonner).start()

    if secondes >= 60:
        duree = f"{secondes // 60} minutes"
    else:
        duree = f"{secondes} secondes"
    return f"Minuteur de {duree} lance."
