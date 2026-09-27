"""Active un profil Jarvis 80/20 orienté latence.

Le script sauvegarde config.yaml avant toute modification, puis réduit uniquement
les coûts de transcription/conversation les plus visibles. Il ne touche ni aux
secrets, ni au mode local/hybride, ni aux intégrations.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

import yaml

RACINE = Path(__file__).resolve().parent.parent
CONFIG = RACINE / "config.yaml"


def _section(conf: dict, nom: str) -> dict:
    valeur = conf.get(nom)
    if not isinstance(valeur, dict):
        valeur = {}
        conf[nom] = valeur
    return valeur


def main() -> None:
    if not CONFIG.exists():
        raise SystemExit("config.yaml introuvable. Lance ce script depuis le dépôt Jarvis.")

    horodatage = datetime.now().strftime("%Y%m%d-%H%M%S")
    sauvegarde = CONFIG.with_name(f"config.backup-80-20-{horodatage}.yaml")
    shutil.copy2(CONFIG, sauvegarde)

    conf = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}

    whisper = _section(conf, "whisper")
    whisper["modele"] = "small"

    assistant = _section(conf, "assistant")
    assistant["duree_suite"] = 4
    assistant["max_tours_outils"] = 3
    assistant["max_appels_outils"] = 6
    assistant["timeout_tour"] = 60

    ollama = _section(conf, "ollama")
    ollama["think"] = False

    CONFIG.write_text(
        yaml.safe_dump(conf, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    print("Profil Jarvis 80/20 activé.")
    print("  Whisper : small")
    print("  Fenêtre de suivi : 4 s")
    print("  Boucles outils : 3 tours / 6 appels max")
    print("  Ollama think : false")
    print(f"Sauvegarde : {sauvegarde.name}")


if __name__ == "__main__":
    main()
