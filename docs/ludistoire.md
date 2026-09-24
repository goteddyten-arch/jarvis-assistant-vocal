# Pont Ludistoire

Jarvis interroge Ludistoire par une API dediee. Il n'accede jamais directement
a MySQL ou D1.

## Statut en lecture seule

Configurer sur le PC qui execute Jarvis :

```powershell
$env:JARVIS_LUDISTOIRE_STATUS_URL = "https://<preprod>/api/jarvis/status"
$env:JARVIS_LUDISTOIRE_TOKEN = "<jeton limite a ludistoire.read>"
```

Le chemin exact doit correspondre a l'endpoint publie par Ludistoire. Le jeton
est optionnel techniquement, mais attendu des que l'endpoint est protege.

Exemples de demandes vocales :

- « Jarvis, quel est l'etat de Ludistoire ? »
- « La Factory est-elle disponible ? »
- « Le catalogue de jouets fonctionne ? »

Cette premiere brique effectue uniquement un `GET`, reste locale et n'est pas
exposee par le serveur MCP de Jarvis. Les missions, publications, suppressions
et migrations ne font pas partie de cet outil.
