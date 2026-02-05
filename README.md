# Butin Maker 🏴‍☠️

Application web pour préparer et automatiser les uploads sur le tracker privé **La Cale**.

## Fonctionnalités

- 🔍 **Recherche TMDB** - Récupération auto des métadonnées (titre, synopsis, poster, note)
- 🏷️ **Renommage auto** - Nom de release selon la nomenclature La Cale
- 🎬 **Création de torrents** - Via qBittorrent avec tracker privé
- 📊 **Génération NFO** - Extraction MediaInfo automatique
- 📝 **Présentation BBCode** - Template La Cale pré-rempli
- 🏷️ **Tags** - Sélection hiérarchique des tags du tracker
- 🚀 **Seed auto** - Lancement du torrent dans qBittorrent

## Déploiement rapide

Créez un fichier `docker-compose.yml` :

```yaml
# Butin Maker 🏴‍☠️
# GitHub: https://github.com/Obtrusive8276/butin-maker

services:
  backend:
    image: ghcr.io/obtrusive8276/butin-maker-backend:latest
    container_name: la-soute
    restart: unless-stopped
    volumes:
      - ./config:/config
      - ./output:/app/output
      - ./tags_data.json:/app/data/tags_data.json:ro
      # Vos fichiers à uploader (lecture seule)
      - /path/to/your/media:/data:ro
    ports:
      - "8000:8000"

  frontend:
    image: ghcr.io/obtrusive8276/butin-maker-frontend:latest
    container_name: le-pont
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      - backend
```

Téléchargez aussi le fichier des tags :
```bash
curl -O https://raw.githubusercontent.com/Obtrusive8276/butin-maker/main/tags_data.json
```

Lancez :
```bash
docker-compose up -d
```

Accès : **http://localhost:3000**

## Configuration

Cliquez sur ⚙️ en haut à droite pour configurer :
- **qBittorrent** : URL, port et identifiants WebUI
- **Tracker** : URL d'annonce avec passkey et URL d'upload
- **TMDB** : Clé API (optionnelle, pour la recherche de films/séries)

## Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `MEDIA_ROOT` | Dossier des médias | `/data` |
| `OUTPUT_DIR` | Dossier de sortie | `/app/output` |
| `CONFIG_DIR` | Dossier config | `/config` |
| `TMDB_API_KEY` | Clé API TMDB | - |

Exemple dans `docker-compose.yml` :
```yaml
environment:
  - TMDB_API_KEY=votre_cle_api
```

## Workflow

1. **Sélection fichiers** - Choisir le média à uploader
2. **TMDB** - Rechercher et sélectionner le film/série
3. **MediaInfo** - Générer le NFO
4. **Renommage** - Valider le nom de release
5. **Torrent** - Créer le fichier .torrent
6. **Finalisation** - Télécharger les fichiers et uploader sur La Cale

## Images supportées

- `linux/amd64` (PC standard)
- `linux/arm64` (Raspberry Pi, Mac M1/M2)
