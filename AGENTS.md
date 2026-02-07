# Butin Maker 🏴‍☠️

## 📋 Description du Projet

Application web **Dockerisée** permettant de préparer et automatiser les uploads sur le tracker privé **La Cale**. L'outil gère :
- La recherche de métadonnées via **TMDB**
- Le **renommage automatique** selon les règles de nomenclature La Cale
- La création de torrents via qBittorrent distant
- La génération de fichiers NFO avec MediaInfo
- La création de présentations formatées en BBCode

---

## 🏗️ Architecture Technique

### Stack Technologique

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| **Backend** | Python 3.11+ / FastAPI | Excellent écosystème pour torrent/mediainfo, async natif, API REST moderne |
| **Frontend** | React 18 + TypeScript | UI réactive, composants réutilisables, typage fort |
| **Styling** | TailwindCSS + shadcn/ui | Design moderne, composants accessibles, développement rapide |
| **Icons** | Lucide React | Iconographie cohérente et légère |
| **State** | Zustand | Gestion d'état simple et performante |
| **API Client** | Axios / TanStack Query | Gestion des requêtes avec cache |

### Structure du Projet

```
la-cale-uploader/
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # Point d'entrée FastAPI
│   │   ├── config.py               # Configuration (settings)
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── files.py            # Explorateur de fichiers
│   │   │   ├── torrent.py          # Gestion qBittorrent
│   │   │   ├── mediainfo.py        # Génération NFO
│   │   │   ├── presentation.py     # Génération présentation
│   │   │   ├── tags.py             # Gestion des tags
│   │   │   ├── settings.py         # Paramètres utilisateur
│   │   │   └── tmdb.py             # Recherche TMDB & Renommage
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── qbittorrent_service.py
│   │   │   ├── mediainfo_service.py
│   │   │   ├── presentation_service.py
│   │   │   ├── file_service.py
│   │   │   ├── tmdb_service.py     # Intégration TMDB
│   │   │   └── naming_service.py   # Nomenclature La Cale
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── torrent.py
│   │   │   ├── media.py
│   │   │   └── settings.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   ├── data/
│   │   ├── tags_data.json          # Données des tags (existant)
│   │   └── settings.json           # Paramètres persistants
│   ├── templates/
│   │   └── presentation_template.txt
│   ├── output/                     # Fichiers générés (.torrent, .nfo)
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                 # Composants shadcn/ui
│   │   │   ├── FileExplorer/
│   │   │   ├── TorrentCreator/
│   │   │   ├── MediaInfoViewer/
│   │   │   ├── PresentationEditor/
│   │   │   ├── utils/               # Utilitaires partagés (formatSize, formatDuration)
│   │   │   └── Settings/
│   │   ├── hooks/
│   │   ├── stores/
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
├── docker-compose.yml
├── .env.example
├── README.md
└── AGENTS.md
```

---

## 🎯 Fonctionnalités Principales

### 1. Explorateur de Fichiers
- Navigation dans l'arborescence du volume Docker monté (`/data`)
- Sélection de fichiers/dossiers pour l'upload
- Affichage de la taille et du type de fichier
- Support multi-sélection
- Filtrage par type de média (vidéo, audio, etc.)
- **Détection automatique des dossiers de séries** (premier fichier vidéo pour MediaInfo)

### 2. Recherche TMDB & Renommage Automatique
- Recherche de films et séries TV via l'API TMDB
- Récupération automatique des métadonnées (titre, année, synopsis, poster, note, genres)
- **Génération du nom de release selon la nomenclature La Cale**
- Détection automatique du groupe depuis le fichier source
- Support des films ET des séries (saisons, épisodes, intégrales)

### 3. Connexion qBittorrent Distant
- Configuration de l'URL, port, identifiants qBittorrent WebUI
- Test de connexion
- Création de torrent avec :
  - Ajout automatique du tracker privé La Cale
  - Paramètres de pièce (piece size) configurables
  - Option "private" activée par défaut
- Récupération du fichier .torrent généré

### 4. Génération NFO avec MediaInfo
- Analyse des fichiers média sélectionnés
- Extraction des métadonnées :
  - Informations vidéo (codec, résolution, bitrate, FPS)
  - Informations audio (codec, canaux, langue)
  - Informations sous-titres
  - Durée, taille du fichier
- Export au format NFO standard

### 5. Génération de Présentation BBCode
- Template configurable (basé sur `Modèle présentation.txt`)
- Champs dynamiques :
  - Titre du contenu
  - Image (poster TMDB/IMDB)
  - Note
  - Genre
  - Synopsis/Description
  - Détails techniques (qualité, format, codecs, langues, sous-titres, taille)
- Prévisualisation en temps réel
- Copie dans le presse-papier

### 6. Système de Tags
- Chargement des tags depuis `tags_data.json`
- Navigation hiérarchique :
  - Catégorie principale → Sous-catégorie → Caractéristiques → Tags
- Sélection multiple avec validation
- Affichage des tags sélectionnés pour copie manuelle

### 7. Paramètres
- **qBittorrent** : URL, port, username, password
- **Tracker** : URL du tracker privé (passkey incluse)
- **Répertoires** : Dossier de sortie pour .torrent et .nfo
- **La Cale** : URL d'upload du tracker
- Sauvegarde persistante des paramètres

### 8. Workflow Final
- Téléchargement du fichier .torrent
- Téléchargement du fichier .nfo
- Copie de la présentation BBCode
- Affichage des tags à sélectionner
- Bouton de redirection vers l'URL d'upload de La Cale

---

## 🔌 Intégrations Externes

### qBittorrent WebUI API
- **Documentation** : https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)
- **Endpoints utilisés** :
  - `POST /api/v2/auth/login` - Authentification
  - `POST /api/v2/torrents/createTorrent` - Création de torrent (non disponible nativement, utiliser la librairie Python)
  - `GET /api/v2/torrents/export` - Export du fichier .torrent

### MediaInfo
- **Librairie Python** : `pymediainfo`
- Nécessite MediaInfo installé sur le système
- Extraction JSON des métadonnées

### TMDB API
- **Documentation** : https://developers.themoviedb.org/3
- **Endpoints utilisés** :
  - `GET /search/multi` - Recherche films et séries
  - `GET /movie/{id}` - Détails d'un film
  - `GET /tv/{id}` - Détails d'une série
- Récupération automatique des posters et métadonnées
- Nécessite une clé API (variable `TMDB_API_KEY`)

---

## 📝 Nomenclature La Cale

### Structure Films

| Type | Format |
|------|--------|
| **SD** | `Titre.Année.Langue.Source.CodecVidéo-Team` |
| **HD** | `Titre.Année.Langue.Résolution.Source.CodecVidéo-Team` |
| **HDR** | `Titre.Année.Langue.Dynamic.Résolution.Source.CodecVidéo-Team` |
| **Complet** | `Titre.Année.Info.Edition.Langue.LangueInfo.Dynamic.Résolution.Source.CodecVidéo-Team` |

**Exemple** : `Gladiator.II.2024.MULTi.VFF.1080p.BluRay.x264-PRODUX`

### Structure Séries

| Type | Format |
|------|--------|
| **Épisode** | `Titre.S##E##.Langue.Résolution.Source.CodecVidéo-Team` |
| **Épisode seul** | `Titre.E##.Langue.Source.CodecVidéo-Team` |
| **Épisode final** | `Titre.S##E##.FiNAL.Langue.Source.CodecVidéo-Team` |
| **Saison** | `Titre.S##.Langue.Source.CodecVidéo-Team` |
| **Intégrale** | `Titre.iNTEGRALE.Langue.Source.CodecVidéo-Team` |

**Exemple** : `Stranger.Things.S01E01.MULTi.1080p.NF.WEB.x264-PRODUX`

### Tags disponibles

| Catégorie | Tags |
|-----------|------|
| **Langue** | MULTi, FRENCH, VOSTFR, SUBFRENCH |
| **LangueInfo** | VFF, VFQ, VFi, VF2, WiTH.AD |
| **Dynamic** | HDR, DV, HDR10Plus, HLG, SDR |
| **Source** | BluRay, WEB, WEBRip, DVDRip, HDTV, REMUX, HDLight |
| **CodecVidéo** | x264, x265, HEVC, H264, H265, AV1 |
| **Info** | REPACK, PROPER, CUSTOM, RERip |
| **Edition** | DC, EXTENDED, REMASTERED, UNRATED, FiNAL.CUT |
| **Plateforme** | NF, AMZN, DSNP, ATVP, HMAX, PMTP, ADN, CR |

### Règles de sanitisation

- Première lettre de chaque mot en majuscule
- Accents supprimés (`é`→`e`, `ç`→`c`)
- Apostrophes remplacées par des points (`L'été`→`L.Ete`)
- Caractères interdits supprimés (`,;{}[]!?`)
- Espaces remplacés par des points
- Groupe détecté automatiquement depuis le fichier source

---

## 📦 Dépendances Backend

```txt
# requirements.txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6
pydantic>=2.5.0
pydantic-settings>=2.1.0
qbittorrent-api>=2024.1.59
pymediainfo>=6.1.0
aiofiles>=23.2.1
python-dotenv>=1.0.0
httpx>=0.26.0
torf>=4.2.4
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

---

## 🖥️ Dépendances Frontend

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.5",
    "zustand": "^4.4.7",
    "lucide-react": "^0.303.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.33"
  }
}
```

---

## 🔄 Workflow Utilisateur

**Ordre des étapes** : `files` → `tmdb` → `nfo` → `rename` → `presentation` → `torrent` → `finalize`

> **Note** : L'étape Tags a été intégrée dans l'écran de Finalisation pour un workflow plus fluide.

```
┌─────────────────────────────────────────────────────────────────┐
│                     ÉTAPE 1: SÉLECTION FICHIERS                 │
│  - Parcourir l'explorateur de fichiers                          │
│  - Sélectionner les fichiers/dossiers à uploader                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ÉTAPE 2: SÉLECTION TMDB                    │
│  - Rechercher le film/série sur TMDB                            │
│  - Sélectionner le bon résultat                                 │
│  - Récupérer les métadonnées (titre, année, synopsis, poster)   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ÉTAPE 3: MEDIAINFO (NFO)                   │
│  - Analyser les fichiers avec MediaInfo (auto)                  │
│  - Générer automatiquement le fichier releasename.nfo           │
│  - Contenu NFO: nom du fichier MKV uniquement (sans chemin)     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ÉTAPE 4: RENOMMAGE                       │
│  - Générer le nom de release selon nomenclature La Cale         │
│  - Nom de release éditable manuellement                         │
│  - Ajuster les options (source, édition, etc.)                  │
│  - Génération automatique du NFO avec le nom de release         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ÉTAPE 5: CRÉATION PRÉSENTATION                │
│  - Remplir les informations (titre, synopsis, etc.)             │
│  - Générer le BBCode selon le template                          │
│  - Prévisualiser et ajuster                                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ÉTAPE 6: CRÉATION TORRENT                   │
│  - Créer le torrent via torf                                    │
│  - Injecter le tracker privé                                    │
│  - Récupérer le fichier .torrent                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ÉTAPE 7: FINALISATION                    │
│  - Télécharger .torrent                                         │
│  - Lancer le seed automatiquement dans qBittorrent              │
│  - Télécharger .nfo (releasename.nfo)                           │
│  - Aperçu NFO et présentation BBCode (rendu visuel)             │
│  - Copier la présentation BBCode                                │
│  - Sélection des tags (Films/Séries) groupés par catégorie      │
│  - Présélection auto basée sur MediaInfo (largeur), TMDB        │
│  - Cliquer sur un tag pour sélectionner/désélectionner          │
│  - Redirection vers La Cale (URL d'upload)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Design UI/UX

### Layout Principal
- **Sidebar gauche** : Navigation entre les étapes
- **Zone centrale** : Contenu de l'étape active
- **Header** : Logo + indicateur de connexion qBittorrent
- **Footer** : Actions contextuelles (suivant, précédent, sauvegarder)

### Thème
- Mode sombre par défaut (adapté aux trackers)
- Couleur principale : Ambre/Or (#eab308) - cohérent avec le template
- Police : Inter ou système

### Composants Clés
- **Stepper** : Progression dans le workflow
- **File Tree** : Explorateur de fichiers interactif
- **Code Preview** : Affichage BBCode avec coloration syntaxique
- **Tag Chips** : Sélection visuelle des tags
- **Toast Notifications** : Feedback utilisateur

---

## ⚙️ Configuration Requise

### Prérequis Système
- **Python** 3.11+
- **Node.js** 18+
- **MediaInfo CLI** installé et accessible dans PATH
- **qBittorrent** avec WebUI activée (peut être distant)

### Variables d'Environnement (.env)

```env
# Backend
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

# qBittorrent (valeurs par défaut, modifiables via UI)
QBITTORRENT_HOST=http://localhost
QBITTORRENT_PORT=8080
QBITTORRENT_USERNAME=admin
QBITTORRENT_PASSWORD=adminadmin

# Tracker La Cale
TRACKER_ANNOUNCE_URL=https://la-cale.example/announce?passkey=YOUR_PASSKEY
LACALE_UPLOAD_URL=https://la-cale.example/upload

# TMDB (optionnel)
TMDB_API_KEY=your_api_key_here
```

---

## 🚀 Lancement

### Docker (Recommandé)

```bash
# Construire et lancer avec docker-compose
docker-compose up -d

# Ou construire manuellement
docker build -t lacale-backend ./backend
docker build -t lacale-frontend ./frontend
```

### Tests Locaux avec Docker

Pour tester localement sans modifier le docker-compose.yml :

```powershell
# 1. Créer les dossiers de config et output (une seule fois)
mkdir C:\Users\Nicolas\Desktop\lacale-config
mkdir C:\Users\Nicolas\Desktop\lacale-output

# 2. Créer le réseau Docker (une seule fois)
docker network create lacale-network

# 3. Build des images
docker build -t la-cale-upload-preparatioin-repo-backend ./backend
docker build -t la-cale-upload-preparatioin-repo-frontend ./frontend

# 4. Lancer le backend avec les volumes mappés
docker run -d --name backend --network lacale-network -p 8000:8000 `
  -v "C:/Users/Nicolas/Downloads:/data:ro" `
  -v "C:/Users/Nicolas/Desktop/lacale-config:/config" `
  -v "C:/Users/Nicolas/Desktop/lacale-output:/app/output" `
  -v "${PWD}/backend/templates:/app/templates:ro" `
  -v "${PWD}/tags_data.json:/app/data/tags_data.json:ro" `
  -e "MEDIA_ROOT=/data" `
  -e "OUTPUT_DIR=/app/output" `
  -e "CONFIG_DIR=/config" `
  la-cale-upload-preparatioin-repo-backend

# 5. Lancer le frontend sur le même réseau
docker run -d --name frontend --network lacale-network -p 3000:80 `
  la-cale-upload-preparatioin-repo-frontend

# 6. Accéder à http://localhost:3000

# Pour arrêter et supprimer les conteneurs :
docker rm -f backend frontend
```

**Volumes Docker :**

| Hôte | Conteneur | Description |
|------|-----------|-------------|
| Dossier médias (ex: Downloads) | `/data` | Fichiers à uploader (lecture seule) |
| Dossier config | `/config` | Paramètres persistants (settings.json) |
| Dossier output | `/app/output` | Fichiers générés (.torrent, .nfo) |

**Variables d'environnement :**

| Variable | Valeur | Description |
|----------|--------|-------------|
| `MEDIA_ROOT` | `/data` | Chemin racine des médias dans le conteneur |
| `CONFIG_DIR` | `/config` | Chemin des paramètres persistants |
| `TMDB_API_KEY` | Clé API | Clé API TMDB pour les métadonnées |

**Connexion qBittorrent depuis Docker :**

Utiliser `host.docker.internal` au lieu de `localhost` pour se connecter à qBittorrent sur la machine hôte.

### Développement (sans Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
python run.py

# Frontend (dans un autre terminal)
cd frontend
npm install
npm run dev
```

---

## 📝 Notes Importantes

1. **Création de torrent** : qBittorrent WebUI ne supporte pas nativement la création de torrent. Utiliser la librairie `torf` côté backend pour créer le .torrent, puis éventuellement l'ajouter à qBittorrent pour le seeding.

2. **Tracker privé** : Le passkey est personnel et ne doit jamais être partagé. Il sera stocké localement dans les settings.

3. **MediaInfo** : Nécessite que les fichiers soient accessibles depuis le serveur backend. Pour des fichiers distants, prévoir un montage réseau ou une copie locale.

4. **Tags La Cale** : La structure des tags est chargée depuis `tags_data.json`. Mettre à jour ce fichier si les tags du tracker changent.

---

## 🔒 Sécurité

- Les credentials qBittorrent et passkey sont stockés localement uniquement
- Pas de transmission vers des serveurs tiers
- CORS configuré pour localhost uniquement en développement
- Validation des entrées utilisateur côté backend

---

## 📄 Fichiers de Référence

- `tags_data.json` : Structure complète des catégories et tags La Cale
- `Modèle présentation.txt` : Template BBCode pour les présentations

---

## 🧪 Tests Unitaires

### Backend (177 tests)

Les tests sont situés dans `backend/tests/` et couvrent :

| Fichier | Description |
|---------|-------------|
| `test_naming_service.py` | Sanitisation titres, détection épisodes, résolution, codecs, langues, **extraction titre séries** |
| `test_realistic_releases.py` | **47 tests** avec noms de releases réalistes (15 films, 15 séries, faux MediaInfo) |
| `test_presentation_service.py` | Génération BBCode, validation template |
| `test_file_service.py` | Extensions média, sécurité chemins |
| `test_tmdb_service.py` | API key, headers, recherches async |
| `test_qbittorrent_service.py` | Connexion, création torrent, seeding |
| `test_mediainfo_service.py` | **Nouveau** - Parsing MediaInfo, génération NFO, durée, exceptions |
| `test_config.py` | **Nouveau** - UserSettings DEFAULTS, load, get (fusion), save, update |
| `test_routers.py` | Validation des routers FastAPI |
| `test_hardlink_existing.py` | **Nouveau** - Gestion des hardlinks existants |
| `conftest.py` | Fixtures partagées |

### Tests Réalistes (`test_realistic_releases.py`)

Tests avec des noms de fichiers provenant de différents trackers pour valider la détection :

**Films testés :**
- Gladiator II, Le Seigneur des Anneaux, Avatar 4K HDR, Dune 2, Intouchables
- Inception REMUX, Astérix et Obélix, The Matrix, Joker, Parasite VOSTFR
- Oppenheimer IMAX, Léon Director's Cut, Amélie Poulain, Interstellar, Spider-Man

**Séries testées :**
- Stranger Things, Game of Thrones, Breaking Bad, La Casa de Papel, The Witcher
- Peaky Blinders, The Mandalorian, Lupin, Dark, Chernobyl
- Squid Game, House of the Dragon, The Last of Us, Wednesday, Severance

**MediaInfo simulés :**
- MULTi.TrueFrench (VFF), MULTi.VFQ (Québec), MULTi.VFi (International)
- 4K HDR HEVC, Dolby Vision, WEB Netflix/Amazon/Disney+
- REMUX DTS-HD MA, SD DVDRip, 720p HDTV, Dolby Atmos

**Exécution des tests :**

```bash
# Dans le conteneur Docker
docker exec backend python -m pytest /app/tests -v

# En local
cd backend
pytest tests/ -v
```

---

## 🔧 Utilitaires Partagés

### Frontend (`src/utils/format.ts`)

```typescript
// Formatage taille fichier
export const formatSize = (bytes: number): string => { ... }

// Formatage durée
export const formatDuration = (seconds: number | null): string => { ... }
```

Ces fonctions sont utilisées par `FileExplorer.tsx` et `MediaInfoViewer.tsx` pour éviter la duplication de code.

---

## 🚀 CI/CD et GitHub Container Registry

### GitHub Actions

Le projet utilise GitHub Actions pour l'intégration continue :

| Workflow | Fichier | Description |
|----------|---------|-------------|
| **CI** | `.github/workflows/ci.yml` | Tests backend + build frontend à chaque push/PR |
| **Docker Publish** | `.github/workflows/docker-publish.yml` | Build et push vers GHCR sur main/tags |

### Images GHCR

Les images Docker sont automatiquement publiées sur GitHub Container Registry :

```bash
# Backend
ghcr.io/OWNER/REPO-backend:latest

# Frontend
ghcr.io/OWNER/REPO-frontend:latest
```

**Plateformes supportées** : `linux/amd64`, `linux/arm64` (Raspberry Pi, Mac M1/M2)

### Déploiement avec GHCR

```bash
# Utiliser docker-compose.ghcr.yml pour les images pré-construites
docker-compose -f docker-compose.ghcr.yml up -d
```

---

## ⚙️ Paramètres Utilisateur (Settings)

### Structure des Settings

Les paramètres sont stockés dans `/config/settings.json` et gérés par `UserSettings` :

```python
DEFAULTS = {
    "qbittorrent": {
        "host": "http://localhost",
        "port": 8080,
        "username": "admin",
        "password": ""
    },
    "tracker": {
        "announce_url": "",
        "upload_url": "https://la-cale.space/upload"
    },
    "paths": {
        "default_browse_path": "",
        "hardlink_path": "",           # Dossier destination des hardlinks
        "qbittorrent_download_path": "", # Dossier téléchargement qBittorrent
        "output_path": ""              # Dossier sortie NFO/.torrent
    },
    "tmdb": {
        "api_key": ""
    }
}
```

### Fusion avec Defaults

La méthode `get()` fusionne automatiquement les settings sauvegardés avec les valeurs par défaut, garantissant que toutes les clés existent même après une mise à jour.

---

## 📝 Notes de Maintenance

### Duplications de Code Identifiées

| Priorité | Problème | Fichiers concernés | Statut | Solution implémentée |
|----------|----------|-------------------|--------|---------------------|
| **Haute** | Fonctions copier presse-papier dupliquées | `Finalize.tsx`, `RenameEditor.tsx`, `MediaInfoViewer.tsx` | ✅ **FAIT** | Hook `useClipboard.ts` créé et utilisé dans tous les composants |
| **Haute** | Logique de détection résolution dupliquée | `naming_service.py`, `MediaInfoViewer.tsx`, `Finalize.tsx` | ✅ **FAIT** | Fonction `getResolutionFromWidth()` extraite dans `utils/format.ts` |
| Moyenne | Méthodes TMDB similaires | `tmdb_service.py` | ✅ **FAIT** | Méthode `_make_request()` générique créée avec helpers `_format_movie_result()` et `_format_tv_result()` |
| Moyenne | Détection langue en double | `naming_service.py` | ⏳ **PAS NÉCESSAIRE** | `detect_language_info()` non utilisée actuellement |
| Basse | Backend helpers.py inutilisé | `helpers.py` | ⏳ **À FAIRE** | Peut être supprimé ou utilisé pour formatage backend |

### Hooks et Utilitaires Créés

#### useClipboard.ts
Hook React réutilisable pour la copie dans le presse-papier :
```typescript
const { copy, copied, error } = useClipboard(timeout?: number);
```
Utilisé dans : `Finalize.tsx`, `RenameEditor.tsx`, `MediaInfoViewer.tsx`

#### getResolutionFromWidth()
Fonction utilitaire dans `utils/format.ts` :
```typescript
export const getResolutionFromWidth = (width: number | null | undefined): string
```
Règles : 3840→2160p, 1920→1080p, 1280→720p, etc.
Utilisée dans : `MediaInfoViewer.tsx`, `Finalize.tsx`

### API Backend - Endpoints Disponibles

#### Fichiers (`/files`)
- `GET /files/root` - Racine du répertoire média
- `GET /files/list?path=&filter_type=` - Liste un répertoire
- `GET /files/info?path=` - Infos sur un fichier
- `GET /files/directory-size?path=` - Taille d'un dossier
- `GET /files/first-video?path=` - Premier fichier vidéo dans un dossier
- `GET /files/video-count?path=` - Nombre de fichiers vidéo
- `GET /files/search?path=&query=&filter_type=` - Recherche de fichiers
- **POST `/files/create-hardlink`** - Création de hardlink (Nouveau)

#### Torrent (`/torrent`)
- `POST /torrent/test-connection` - Test connexion qBittorrent
- `POST /torrent/create` - Création d'un torrent
- `GET /torrent/download/{filename}` - Téléchargement du fichier .torrent
- `POST /torrent/add-for-seeding` - Ajout pour seeding

#### MediaInfo (`/mediainfo`)
- `GET /mediainfo/analyze?path=` - Analyse MediaInfo
- `GET /mediainfo/raw?path=` - Output brut MediaInfo
- `POST /mediainfo/generate-nfo?path=&release_name=` - Génération NFO
- `GET /mediainfo/download-nfo/{filename}` - Téléchargement NFO

#### TMDB (`/tmdb`)
- `GET /tmdb/status` - Statut configuration API
- `GET /tmdb/search?query=&type=` - Recherche films/séries
- `GET /tmdb/movie/{movie_id}` - Détails film
- `GET /tmdb/tv/{tv_id}` - Détails série
- `POST /tmdb/generate-name` - Génération nom de release
- `GET /tmdb/detect-episode?filename=` - Détection saison/épisode
- `GET /tmdb/extract-title?filename=` - Extraction titre
- `GET /tmdb/search-from-filename?filename=&type=` - Recherche depuis nom fichier

#### Présentation (`/presentation`)
- `POST /presentation/generate` - Génération BBCode
- `GET /presentation/template` - Récupération template
- `POST /presentation/template` - Sauvegarde template

#### Tags (`/tags`)
- `GET /tags/` - Tous les tags
- `GET /tags/categories` - Catégories principales
- `GET /tags/category/{slug}` - Détails catégorie
- `GET /tags/subcategories/{category_slug}` - Sous-catégories

#### Settings (`/settings`)
- `GET /settings/` - Récupération settings
- `POST /settings/` - Sauvegarde settings
- `PATCH /settings/qbittorrent` - Mise à jour qBittorrent
- `PATCH /settings/tracker` - Mise à jour tracker

---

## 🔍 Checklist Code Review (à corriger)

### Backend - Critique / Haute priorité

- [x] **Sécurité - Path traversal `file_service.py`** : Ajouter `_is_path_allowed()` dans `get_file_info()`, `get_directory_size()`, `get_first_video_file()`, `count_video_files()`
- [x] **Sécurité - Path traversal `file_service.py`** : Valider que `destination_path` dans `create_hardlink()` est dans un répertoire autorisé
- [x] **Sécurité - Path traversal `routers/torrent.py`** : Protéger `download_torrent()` - valider que le path résolu est dans `output_path`
- [x] **Sécurité - Path traversal `routers/mediainfo.py`** : Protéger `download_nfo()` - même protection
- [x] **Bug - `config.py`** : `_load()` utilise `.copy()` (shallow). Utiliser `copy.deepcopy()` pour éviter la mutation de `DEFAULTS`
- [x] **Bug - `config.py`** : `get()` merge écrase les valeurs vides volontaires (empty string remplacé par default). Distinguer clé absente vs valeur vide
- [x] **Performance - `qbittorrent_service.py`** : `t.generate()` bloque l'event loop async. Exécuter dans `asyncio.to_thread()`
- [x] **Bug - `qbittorrent_service.py`** : `host = host or ...` fait que `host=""` ou `port=0` passent au default. Utiliser `if host is not None`
- [x] **Bug - `qbittorrent_service.py`** : Paramètre `content_path` dans `add_torrent_for_seeding()` est accepté mais jamais utilisé
- [x] **Performance - `tmdb_service.py`** : Nouveau `httpx.AsyncClient` créé à chaque requête. Créer un client unique réutilisable avec timeout
- [x] **Sécurité - `routers/settings.py`** : Les endpoints PATCH acceptent `dict` brut sans validation. Utiliser les modèles Pydantic

### Backend - Moyenne priorité

- [x] **Debug - `routers/tmdb.py`** : Supprimer les `print(f"[DEBUG]...")` en production
- [x] **Code quality - `file_service.py`** : Bare `except:` attrape tout (SystemExit, etc.). Remplacer par `except Exception:`
- [x] **Typo - `naming_service.py`** : `"vvc": "VCC"` devrait être `"VVC"`
- [x] **Bug - `naming_service.py`** : Faux positifs détection plateforme/source par substring (`"max"` matche `"maximum"`). Utiliser des word boundaries regex
- [x] **Config - `main.py`** : CORS origins hardcodés. Rendre configurable via variable d'environnement
- [x] **Logging - `tmdb_service.py`** : Erreurs TMDB avalées silencieusement (401/404 retournent tous `None`). Logger le status + body
- [x] **Performance - `routers/tags.py`** : `tags_data.json` relu et parsé à chaque requête. Mettre en cache + rendre le path configurable
- [x] **API - `routers/files.py`, `torrent.py`, `mediainfo.py`** : Retournent HTTP 200 avec JSON erreur. Utiliser `HTTPException(status_code=404)`
- [x] **Code quality - `mediainfo_service.py`** : Double `MI.parse()` inutile. Supprimer le premier appel
- [x] **Code quality** : Remplacer tous les `print()` par le module `logging`

### Backend - Basse priorité

- [x] **Dead code - `main.py`** : Imports morts `StaticFiles` et `Path`. Supprimer
- [x] **Config - `run.py`** : `reload=True` ne devrait pas être actif en production. Conditionner via env var `DEBUG`

### Frontend - Critique / Haute priorité

- [x] **Sécurité XSS - `Finalize.tsx`** : `[url=javascript:alert(1)]` passe dans `bbcodeToHtml` et produit un `<a href="javascript:...">`. Valider que les URLs commencent par `http://` ou `https://`
- [x] **Bug - `FileExplorer.tsx`** : `handleGlobalSearch` n'a pas de `catch` - l'erreur API est silencieuse, le spinner disparaît sans feedback
- [x] **Bug - `TMDBSearch.tsx`** : Cast unsafe `e.target.value as 'movie' | 'tv' | undefined || undefined`. Utiliser une conversion explicite
- [x] **Anti-pattern - `RenameEditor.tsx`** : `mutate()` appelé dans `useEffect` avec deps incomplètes. Risque de boucle infinie. Refactorer

### Frontend - Moyenne priorité

- [x] **Bug - `format.ts`** : `formatDuration(0)` retourne `'N/A'` car `!0` est truthy. Utiliser `=== null || === undefined`
- [x] **Bug - `RenameEditor.tsx`** : Hardlink path hardcodé `/data/` au lieu de `settings?.paths?.hardlink_path`
- [x] **Bug - `RenameEditor.tsx`** : `season || undefined` convertit saison 0 (spécials) en `undefined`. Utiliser `??`
- [x] **Bug - `TorrentCreator.tsx`** : `trackerUrl` initialisé une fois au mount, pas synchronisé si settings changent
- [x] **Bug - `SettingsModal.tsx`** : `parseInt("")` retourne `NaN` envoyé au backend si le champ port est vidé
- [x] **Bug - `useClipboard.ts`** : `setTimeout` qui reset `copied` n'est jamais clear. setState sur composant démonté possible
- [x] **UX - `Sidebar.tsx`** : Étapes marquées "complétées" par position et non par état réel. Sauter une étape la marque verte
- [x] **UX - `TMDBSelect.tsx`** : Pas de guard si aucun fichier sélectionné. L'utilisateur peut chercher TMDB sans fichier, les étapes suivantes planteront
- [x] **Sécurité - `Finalize.tsx`** : `[img]` injecte des URLs externes sans restriction (tracking IP possible)

### Frontend - Basse priorité

- [x] **Texte - `SettingsModal.tsx`** : Texte d'aide du champ "Dossier de sortie" est un copier-coller du champ hardlink
- [x] **Dead code - `api.ts`** : `renameFile` défini mais jamais appelé
- [x] **Debug - `RenameEditor.tsx`** : `console.log` laissés en production

---

## 🚨 TODO - Corrections Critiques (2026-02-06)

### ✅ Tous les problèmes critiques ont été corrigés ! (2026-02-06)

#### ✅ RÉSOLU - XSS via dangerouslySetInnerHTML
**Fichier**: `frontend/src/components/Finalize.tsx:478, 611`  
**Problème**: Utilisation de `dangerouslySetInnerHTML` avec HTML généré depuis du BBCode sans DOMPurify  
**Impact**: Injection JavaScript, vol de cookies/session, redirection vers sites malveillants  
**Solution appliquée**:
- ✅ `dompurify` et `@types/dompurify` installés
- ✅ `DOMPurify.sanitize()` ajouté aux 2 usages de `dangerouslySetInnerHTML`
- ✅ Protection complète contre les injections XSS

#### ✅ RÉSOLU - Anti-pattern useEffect + mutate
**Fichier**: `frontend/src/components/RenameEditor.tsx:87-93`  
**Problème**: Appel de mutation API dans useEffect avec gestion d'état complexe  
**Impact**: Boucle infinie potentielle, rendus inutiles, comportement imprévisible  
**Solution appliquée**:
- ✅ Refactorisation complète avec `useCallback` pour la génération
- ✅ Toutes les dépendances ajoutées : `source`, `edition`, `info`, `language`
- ✅ **Régénération automatique restaurée** : changement d'options → mise à jour automatique du nom
- ✅ Protection contre les boucles infinies avec flag `hasGenerated`

#### ✅ RÉSOLU - Logger manquant
**Fichier**: `backend/app/services/presentation_service.py:81`  
**Problème**: Utilisation de `print()` au lieu de `logging`  
**Impact**: Logs perdus en production, pas de niveau de sévérité  
**Solution appliquée**:
- ✅ Import du module `logging`
- ✅ Création du logger : `logger = logging.getLogger(__name__)`
- ✅ Remplacement de `print()` par `logger.error()` avec `exc_info=True`

#### ✅ RÉSOLU - Port invalide par défaut
**Fichier**: `frontend/src/components/SettingsModal.tsx:110`  
**Problème**: `parseInt(e.target.value) || 0` retourne 0 si champ vide  
**Impact**: Port 0 invalide, connexion qBittorrent impossible  
**Solution appliquée**:
- ✅ Changement de `|| 0` en `|| 8080`
- ✅ Port par défaut valide restauré

#### ✅ RÉSOLU - Code mort
**Fichier**: `frontend/src/services/api.ts:302-313`  
**Problème**: Fonction `renameFile` définie mais jamais appelée  
**Impact**: Confusion, maintenance inutile  
**Solution appliquée**:
- ✅ Fonction `renameFile` supprimée (12 lignes)
- ✅ Code nettoyé et maintenu

## Étape 2 - Upload Automatique vers La Cale 🏴‍☠️

### 🎯 Vue d'ensemble

Implémentation complète de l'upload automatique vers le tracker La Cale via son API REST. Cette fonctionnalité permettra d'uploader directement depuis l'application sans passer par l'interface web du tracker.

**Méthodologie** : TDD strict - Tous les tests écrits AVANT l'implémentation  
**Branche** : `beta` (isolée de `main` jusqu'à validation complète)  
**Exigence** : 100% des tests doivent passer avant merge  
**Règle Git** : Ne jamais commit/push sans demande explicite de l'utilisateur

---

### 📦 Dépendances

**Backend** : Aucune dépendance supplémentaire (httpx et aiofiles déjà présents)  
**Frontend** : Aucune dépendance supplémentaire (axios et @tanstack/react-query déjà présents)

---

### 🗂️ Structure des fichiers

#### Backend - Nouveaux fichiers ✨

```
backend/
├── app/
│   ├── services/
│   │   └── lacale_service.py          # Service API La Cale
│   ├── routers/
│   │   └── lacale.py                  # Endpoints La Cale
│   └── models/
│       └── lacale.py                  # Modèles Pydantic
└── tests/
    ├── test_lacale_service.py         # Tests service (25 tests)
    └── test_lacale_router.py          # Tests router (12 tests)
```

#### Backend - Fichiers modifiés 🔧

```
backend/
├── app/
│   ├── config.py                      # +1 ligne (lacale_api_key)
│   ├── main.py                        # +2 lignes (import + register router)
│   └── services/
│       └── qbittorrent_service.py     # +1 ligne (source=lacale)
└── tests/
    ├── test_config.py                 # +3 tests
    └── test_qbittorrent_service.py    # +4 tests
```

#### Frontend - Fichiers modifiés 🔧

```
frontend/src/
├── types/index.ts                     # +50 lignes (types La Cale)
├── services/api.ts                    # +20 lignes (lacaleApi)
├── stores/appStore.ts                 # +10 lignes (état upload)
├── components/
│   ├── SettingsModal.tsx              # +15 lignes (champ API key)
│   └── Finalize.tsx                   # +150 lignes (upload auto)
```

---

### 🧪 PHASE 1 : TESTS (TDD)

#### 1.1 - Tests Backend Config (`test_config.py`)

**Ajouts** : 3 tests supplémentaires

```python
def test_user_settings_defaults_include_lacale_api_key():
    """Vérifie que DEFAULTS contient tracker.lacale_api_key"""
    assert "tracker" in UserSettings.DEFAULTS
    assert "lacale_api_key" in UserSettings.DEFAULTS["tracker"]
    assert UserSettings.DEFAULTS["tracker"]["lacale_api_key"] == ""

def test_user_settings_get_returns_lacale_api_key():
    """Vérifie que get() retourne lacale_api_key même si absent du JSON"""
    us = UserSettings()
    us._data = {"tracker": {"announce_url": "http://test"}}
    result = us.get()
    assert "lacale_api_key" in result["tracker"]
    assert result["tracker"]["lacale_api_key"] == ""

def test_user_settings_save_lacale_api_key():
    """Vérifie que l'API key est bien sauvegardée"""
    us = UserSettings()
    data = us.get()
    data["tracker"]["lacale_api_key"] = "test_api_key_123"
    us.save(data)
    us2 = UserSettings()
    result = us2.get()
    assert result["tracker"]["lacale_api_key"] == "test_api_key_123"
```

**Temps estimé** : 30 min

---

#### 1.2 - Tests Backend qBittorrent (`test_qbittorrent_service.py`)

**Ajouts** : 4 tests supplémentaires

```python
@pytest.mark.asyncio
async def test_create_torrent_adds_source_flag_lacale():
    """Vérifie que create_torrent ajoute automatiquement source=lacale"""
    service = QBittorrentService()
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.mkv"
        test_file.write_bytes(b"fake video content")
        success, result = await service.create_torrent(str(test_file))
        assert success
        t = torf.Torrent.read(result["torrent_path"])
        assert t.source == "lacale"

@pytest.mark.asyncio
async def test_create_torrent_source_flag_case_sensitive():
    """Vérifie que le flag source est exactement 'lacale' (minuscules)"""
    # Test que source == "lacale" et non "LaCale" ou "LACALE"

@pytest.mark.asyncio
async def test_create_torrent_preserves_existing_params():
    """Vérifie que source=lacale ne casse pas les autres paramètres"""
    # Test private, piece_size, tracker_url préservés

@pytest.mark.asyncio
async def test_create_torrent_source_flag_with_directory():
    """Vérifie que source=lacale fonctionne aussi pour les dossiers"""
```

**Temps estimé** : 1h

---

#### 1.3 - Tests Backend Service La Cale (`test_lacale_service.py`)

**Nouveaux tests** : 25 tests complets

**Catégories** :
- Configuration (3 tests) : init avec/sans API key, custom base URL
- Headers (2 tests) : avec/sans API key
- Fetch Meta (6 tests) : succès, 401, 403, 500, timeout, parsing
- Find Category (3 tests) : movie, tv, not found
- Upload (11 tests) : succès, 409, 429, fichier manquant, multipart, etc.

**Temps estimé** : 3h

---

#### 1.4 - Tests Backend Router (`test_lacale_router.py`)

**Nouveaux tests** : 12 tests

**Endpoints testés** :
- `GET /lacale/meta` (3 tests) : succès, sans API key, API key invalide
- `GET /lacale/category` (3 tests) : movie, tv, type invalide
- `POST /lacale/upload` (6 tests) : succès, champs manquants, 409, 429

**Temps estimé** : 2h

---

#### 📊 Récapitulatif Tests Phase 1

| Fichier | Tests existants | Tests à ajouter | Total | Temps |
|---------|----------------|-----------------|-------|-------|
| `test_config.py` | ~15 | +3 | ~18 | 30 min |
| `test_qbittorrent_service.py` | ~20 | +4 | ~24 | 1h |
| `test_lacale_service.py` | 0 | +25 | 25 | 3h |
| `test_lacale_router.py` | 0 | +12 | 12 | 2h |
| **TOTAL** | **~35** | **+44** | **~79** | **6h 30min** |

---

### 🚀 PHASE 2 : IMPLÉMENTATION

#### 2.1 - Backend Config

**Fichier** : `backend/app/config.py` (ligne 72-76)

```python
"tracker": {
    "announce_url": "",
    "upload_url": "https://la-cale.space/upload",
    "lacale_api_key": ""  # ← AJOUTER
},
```

**Tests validés** : 3 nouveaux tests  
**Temps estimé** : 15 min

---

#### 2.2 - Backend qBittorrent Service

**Fichier** : `backend/app/services/qbittorrent_service.py` (ligne 82)

```python
t = torf.Torrent(path=source_path)
t.name = content_name
t.private = private
t.source = "lacale"  # ← AJOUTER (Important pour éviter re-téléchargement)
```

**Tests validés** : 4 nouveaux tests  
**Temps estimé** : 20 min

---

#### 2.3 - Backend Modèles Pydantic

**Fichier** : `backend/app/models/lacale.py` ✨ NOUVEAU

**Contenu** :
- `LaCaleTag` : id, name, slug
- `LaCaleTagGroup` : id, name, slug, order, tags[]
- `LaCaleCategory` : id, name, slug, icon, parentId, children[]
- `LaCaleMetaResponse` : categories[], tagGroups[], ungroupedTags[]
- `LaCaleUploadRequest` : title, category_id, torrent_file_path, tag_ids[], description, tmdb_id, tmdb_type, cover_url, nfo_file_path
- `LaCaleUploadResponse` : success, id, slug, link, error

**Temps estimé** : 30 min

---

#### 2.4 - Backend Service La Cale

**Fichier** : `backend/app/services/lacale_service.py` ✨ NOUVEAU (~250 lignes)

**Méthodes principales** :
- `__init__(api_key, base_url)` : Initialisation avec API key depuis settings
- `_get_headers()` : Construit headers avec `X-Api-Key`
- `fetch_meta()` : GET /api/external/meta → LaCaleMetaResponse
- `find_category_id(content_type)` : Trouve "cat_films" ou "cat_series"
- `upload(request)` : POST /api/external/upload (multipart/form-data)

**Gestion erreurs** :
- 401 Unauthorized : API key invalide
- 403 Forbidden : API key révoquée
- 409 Conflict : Torrent déjà existant
- 429 Rate Limit : 30 req/min dépassé (message clair)
- 500 Server Error : Erreur serveur

**Tests validés** : 25 tests  
**Temps estimé** : 2h

---

#### 2.5 - Backend Router La Cale

**Fichier** : `backend/app/routers/lacale.py` ✨ NOUVEAU (~120 lignes)

**Endpoints** :
- `GET /lacale/meta` : Récupère catégories + tags
- `GET /lacale/category?type=movie|tv` : Retourne category_id
- `POST /lacale/upload` : Upload torrent (body: LaCaleUploadRequest)

**Tests validés** : 12 tests  
**Temps estimé** : 1h

---

#### 2.6 - Backend Main

**Fichier** : `backend/app/main.py`

```python
# Ligne ~15 - Ajouter import
from .routers import files, torrent, mediainfo, tmdb, presentation, tags, settings, lacale

# Ligne ~30 - Enregistrer router
app.include_router(lacale.router, prefix="/api")
```

**Temps estimé** : 5 min

---

#### 2.7 - Frontend Types

**Fichier** : `frontend/src/types/index.ts` (après ligne 43)

**Ajouts** :
- `LaCaleTag`, `LaCaleTagGroup`, `LaCaleCategory`
- `LaCaleMetaResponse`, `LaCaleUploadRequest`, `LaCaleUploadResponse`
- Modification `TrackerSettings` : ajouter `lacale_api_key: string`

**Temps estimé** : 15 min

---

#### 2.8 - Frontend API Client

**Fichier** : `frontend/src/services/api.ts` (après ligne ~180)

```typescript
export const lacaleApi = {
  getMeta: async (): Promise<LaCaleMetaResponse> => { ... },
  getCategoryId: async (type: 'movie' | 'tv'): Promise<string> => { ... },
  upload: async (request: LaCaleUploadRequest): Promise<LaCaleUploadResponse> => { ... },
};
```

**Temps estimé** : 20 min

---

#### 2.9 - Frontend Store

**Fichier** : `frontend/src/stores/appStore.ts`

**Ajouts** :
- `uploadStatus: 'idle' | 'loading' | 'success' | 'error'`
- `uploadResult: LaCaleUploadResponse | null`
- `uploadError: string | null`
- Setters associés

**Temps estimé** : 15 min

---

#### 2.10 - Frontend Settings Modal

**Fichier** : `frontend/src/components/SettingsModal.tsx` (après upload_url)

```tsx
<div>
  <label className="block text-sm font-medium text-gray-300 mb-2">
    Clé API La Cale
  </label>
  <input
    type="password"
    value={formData.tracker.lacale_api_key}
    onChange={(e) => setFormData({
      ...formData,
      tracker: { ...formData.tracker, lacale_api_key: e.target.value }
    })}
    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
    placeholder="Votre clé API La Cale"
  />
  <p className="mt-1 text-sm text-gray-400">
    Générez votre clé API dans les paramètres de votre compte La Cale.
  </p>
</div>
```

**Temps estimé** : 20 min

---

#### 2.11 - Frontend Finalize (Upload Auto)

**Fichier** : `frontend/src/components/Finalize.tsx` (+150 lignes)

**Modifications principales** :
1. Import `lacaleApi` et types
2. États : `uploadStatus`, `uploadError`, `uploadLink`
3. Mutation `uploadMutation` avec TanStack Query :
   - Auto-détection `categoryId` via `lacaleApi.getCategoryId(contentType)`
   - Construction `LaCaleUploadRequest` avec tous les champs
   - Gestion `onSuccess` / `onError`
4. UI Upload :
   - Bouton "Upload automatique" (idle)
   - Spinner + texte (loading)
   - Lien vers torrent + badge succès (success)
   - Message erreur + bouton réessayer (error)
   - Warning si API key manquante
5. Fallback : Bouton "Upload manuel" (ancien comportement)

**Messages d'erreur spécifiques** :
- 401 : "API key invalide"
- 409 : "Torrent déjà existant"
- 429 : "Limite 30 req/min dépassée. Veuillez patienter."

**Temps estimé** : 2h

---

#### 📊 Récapitulatif Implémentation Phase 2

| Fichier | Type | Temps |
|---------|------|-------|
| `config.py` | Modification | 15 min |
| `qbittorrent_service.py` | Modification | 20 min |
| `models/lacale.py` | Nouveau | 30 min |
| `services/lacale_service.py` | Nouveau | 2h |
| `routers/lacale.py` | Nouveau | 1h |
| `main.py` | Modification | 5 min |
| `types/index.ts` | Modification | 15 min |
| `api.ts` | Modification | 20 min |
| `appStore.ts` | Modification | 15 min |
| `SettingsModal.tsx` | Modification | 20 min |
| `Finalize.tsx` | Modification | 2h |
| **TOTAL** | | **~7h** |

---

### ✅ PHASE 3 : VALIDATION

#### 3.1 - Tests automatisés

```bash
# Backend - Tous les tests
pytest tests/ -v --cov=app --cov-report=term-missing

# Tests spécifiques La Cale
pytest tests/test_lacale_service.py -v
pytest tests/test_lacale_router.py -v

# Vérifier couverture 100%
pytest tests/test_lacale_service.py --cov=app.services.lacale_service --cov-report=term-missing
```

**Critère** : 100% des tests passent (79 tests total)  
**Temps estimé** : 1h (debug + corrections)

---

#### 3.2 - Tests manuels Docker

```bash
# Build images beta
docker build -t la-cale-backend:beta ./backend
docker build -t la-cale-frontend:beta ./frontend

# Run conteneurs beta
docker run -d --name backend-beta --network lacale-network -p 8001:8000 \
  -v "C:/Users/Nicolas/Downloads:/data:ro" \
  -v "C:/Users/Nicolas/Desktop/lacale-config:/config" \
  -v "C:/Users/Nicolas/Desktop/lacale-output:/app/output" \
  la-cale-backend:beta

docker run -d --name frontend-beta --network lacale-network -p 3001:80 \
  la-cale-frontend:beta

# Accès: http://localhost:3001
```

**Scénarios à tester** :
1. ✅ Configurer API key dans Settings
2. ✅ Workflow complet : Files → TMDB → Rename → Torrent → Upload
3. ✅ Vérifier `source=lacale` dans .torrent créé
4. ✅ Upload film réussi (lien retourné)
5. ✅ Upload série réussie (lien retourné)
6. ✅ Erreur API key manquante (message clair)
7. ✅ Erreur API key invalide (401)

**Temps estimé** : 2h

---

### 🌳 PHASE 4 : GIT & BRANCHING

#### 4.1 - Création branche beta

```bash
git checkout main
git pull origin main
git checkout -b beta
```

---

#### 4.2 - Structure des commits

**Ordre recommandé** (8 commits) :

1. **Tests config + qbittorrent** (7 tests)
   ```
   test: Ajout tests TDD pour API key La Cale et source flag
   ```

2. **Tests service + router** (37 tests)
   ```
   test: Ajout tests TDD service et router La Cale (37 tests)
   ```

3. **Backend config + qbittorrent**
   ```
   feat: Ajout lacale_api_key dans settings + source flag
   ```

4. **Backend modèles + service**
   ```
   feat: Implémentation service API La Cale
   ```

5. **Backend router + main**
   ```
   feat: Ajout endpoints API La Cale
   ```

6. **Frontend types + API**
   ```
   feat: Types et client API La Cale (frontend)
   ```

7. **Frontend store + settings**
   ```
   feat: État upload et configuration API key (frontend)
   ```

8. **Frontend Finalize**
   ```
   feat: Implémentation upload automatique vers La Cale
   ```

9. **Documentation**
   ```
   docs: Plan détaillé implémentation upload auto La Cale
   ```

**⚠️ IMPORTANT** : Ne jamais commit/push sans demande explicite de l'utilisateur !

---

#### 4.3 - Pull Request (draft)

```bash
gh pr create --base main --head beta \
  --title "feat: Upload automatique vers La Cale (API)" \
  --draft
```

**Contenu PR** :
- Checklist : Tests, implémentation, validation
- Instructions tests Docker
- Liste fichiers modifiés
- ⚠️ Mode DRAFT jusqu'à validation utilisateur

**Temps estimé** : 1h

---

### 📈 ESTIMATION TOTALE

| Phase | Description | Temps |
|-------|-------------|-------|
| Phase 1 | Tests TDD (44 tests) | 6h 30min |
| Phase 2 | Implémentation | 7h |
| Phase 3 | Validation | 3h |
| Phase 4 | Git + PR | 1h |
| **TOTAL** | | **~17h 30min** |

**Répartition recommandée** :
- Jour 1 (4h) : Tests TDD (config, qbittorrent, début lacale_service)
- Jour 2 (4h) : Tests TDD (fin lacale_service, lacale_router)
- Jour 3 (4h) : Implémentation backend
- Jour 4 (3h) : Implémentation frontend
- Jour 5 (2h 30min) : Validation + Git

---

### 🎯 CRITÈRES DE SUCCÈS

#### Tests automatisés
- ✅ 100% des tests backend passent (79 tests)
- ✅ Couverture ≥ 90% sur `lacale_service.py` et `lacale.py`
- ✅ Source flag `lacale` présent dans tous les torrents

#### Tests manuels
- ✅ Upload film/série réussi avec lien
- ✅ Gestion erreurs : API key manquante, 401, 409, 429
- ✅ Messages clairs et actionnables

#### Expérience utilisateur
- ✅ Workflow fluide sans friction
- ✅ Fallback upload manuel si problème
- ✅ API key sécurisée (type password)

---

### 🚨 POINTS D'ATTENTION

#### Sécurité
- ⚠️ **API key** : Stockée en clair dans `settings.json` (local uniquement)
- ⚠️ **Path traversal** : Vérifier chemins `torrent_file_path` et `nfo_file_path`
- ⚠️ **Rate limiting** : Message clair, pas de retry auto

#### Performance
- ⚠️ **Timeout** : 30s par défaut (configurable)
- ⚠️ **Multipart** : Upload peut être lent pour gros fichiers

#### Compatibilité
- ⚠️ **API La Cale** : Dépendance externe - si API change, adapter modèles
- ⚠️ **Tags** : Structure différente de `tags_data.json`

---

### 📚 RESSOURCES

- **API La Cale** : `LA_CALE_API.md`
- **Exemple upload** : Node.js (ligne 173-201)
- **Endpoint meta** : GET /api/external/meta (ligne 71-83)
- **Endpoint upload** : POST /api/external/upload (ligne 92-131)

---

### ❓ QUESTIONS OUVERTES

1. **Tags dynamiques** : Supprimer `tags_data.json` après migration API ?
2. **Cache meta** : Mettre en cache `/api/external/meta` frontend ?
3. **Multi-upload** : Gérer file d'attente pour batch uploads ?

---

### 📝 CLARIFICATIONS RÉSOLUES

| Question | Réponse |
|----------|---------|
| Source flag torrent ? | ✅ Oui, ajouter `t.source = "lacale"` automatiquement |
| Gestion tags ? | ✅ Option A - Récupérer dynamiquement via `/meta` (films vs séries) |
| API key vs passkey ? | ✅ Une seule API key (header `X-Api-Key`) - passkey obsolète |
| Détection catégorie ? | ✅ Auto selon `contentType` (movie→Films, tv→Séries) |
| Position bouton upload ? | ✅ Option A - Dans `Finalize.tsx` existant |
| Gestion rate limit ? | ✅ Afficher erreur claire, pas de retry auto |
| Niveau tests ? | ✅ Maximum de tests TDD, 100% doivent passer |
| Stockage API key ? | ✅ Option A - `tracker.lacale_api_key` |
| Branche beta ? | ✅ Tout sur beta, merge main après validation utilisateur |

---

## Étape 3 - Migration Tags vers API Dynamique 🏷️

### 🎯 Vue d'ensemble

Remplacement du fichier statique `tags_data.json` par l'endpoint dynamique `/api/external/meta` de La Cale. Les tags seront récupérés en temps réel, filtrés par type de contenu (Films vs Séries), et mis en cache côté frontend (TanStack Query + localStorage).

**Objectif** : Supprimer toute dépendance à `tags_data.json` et utiliser exclusivement l'API La Cale comme source de vérité pour les catégories et tags.

**Méthodologie** : TDD strict — tests d'abord, implémentation ensuite  
**Branche** : `beta`  
**Exigence** : 100% des tests doivent passer avant commit

---

### 📊 Mapping des structures de données

#### Ancienne structure (`tags_data.json`)

```
quaiprincipalcategories[] → emplacementsouscategorie[] → caracteristiques[] → tags[]
         (Vidéo)                 (Films / Séries)            (Qualité vidéo)      (1080p)
```

Champs utilisés :
- `category.slug` : `"video"`
- `subCategory.slug` : `"films"` ou `"series"`
- `caracteristique.name` : nom du groupe (ex: "Qualité vidéo")
- `tag.name` : nom du tag (ex: "1080p") — utilisé comme identifiant

#### Nouvelle structure (API `/meta`)

```
categories[] → children[]        tagGroups[] → tags[]       ungroupedTags[]
  (Vidéo)       (Films/Séries)    (Qualité vidéo)  (1080p)
```

Champs utilisés :
- `category.slug` : `"video"`
- `child.slug` : `"films"` ou `"series"`
- `child.id` : `"cat_films"` ou `"cat_series"` — pour `categoryId` de l'upload
- `tagGroup.name` : nom du groupe (ex: "Qualité vidéo")
- `tagGroup.tags[].id` : **ID du tag** — utilisé pour l'upload (`tags=TAG_ID`)
- `tagGroup.tags[].name` : nom affiché
- `tagGroup.tags[].slug` : slug du tag

#### Différences clés

| Aspect | Ancien (`tags_data.json`) | Nouveau (API `/meta`) |
|--------|--------------------------|----------------------|
| **Identifiant tag** | `tag.name` (string) | `tag.id` (string unique) |
| **Groupement** | `caracteristiques[]` | `tagGroups[]` |
| **Filtrage Films/Séries** | Sous-catégorie dans la hiérarchie | Pas de filtrage natif par catégorie dans tagGroups |
| **Persistance** | Fichier statique embarqué | API dynamique + cache localStorage |
| **Mise à jour** | Manuelle (modifier fichier) | Automatique (API) |

#### Stratégie de filtrage

L'API `/meta` retourne **tous** les tagGroups sans distinction Films/Séries. Deux approches possibles :
- **Option A** : Afficher tous les tagGroups (simpler, l'utilisateur choisit)
- **Option B** : Filtrer côté frontend selon le `contentType` sélectionné

**Décision** : Option A — Afficher tous les tagGroups. Le tracker gère la validation côté serveur. Les tags non applicables seront simplement ignorés.

---

### 🗂️ Structure des fichiers

#### Nouveaux fichiers ✨

```
frontend/src/
├── utils/
│   └── tagsAdapter.ts                 # Adaptateur ancien format → nouveau format
└── hooks/
    └── useCachedTags.ts               # Hook avec cache localStorage + TanStack Query
```

#### Fichiers modifiés 🔧

```
backend/
├── app/main.py                        # Supprimer import/register tags router
├── Dockerfile                         # Supprimer COPY tags_data.json
frontend/src/
├── components/Finalize.tsx            # Remplacer tagsApi → lacaleApi.getMeta()
├── components/Finalize.test.tsx       # Adapter mocks
├── services/api.ts                    # Supprimer tagsApi
├── types/index.ts                     # Ajouter types API meta, supprimer anciens types tags
```

#### Fichiers supprimés ❌

```
backend/app/routers/tags.py            # Router tags statique
backend/tests/test_tags_router.py      # Tests du router supprimé (si existant)
```

#### Fichiers archivés 📦

```
tags_data.json → tags_data.json.archive    # Renommer (pas supprimer)
```

---

### 🧪 PHASE 1 : TESTS

#### 1.1 - Tests Frontend : `useCachedTags.ts`

**Fichier** : `frontend/src/hooks/useCachedTags.test.ts` ✨ NOUVEAU

```typescript
// Tests à écrire :
// 1. Retourne les données depuis l'API quand le cache est vide
// 2. Retourne les données depuis localStorage quand l'API échoue
// 3. Met à jour localStorage après un fetch réussi
// 4. Respecte le staleTime de 1h (ne refetch pas avant)
// 5. Retourne état loading pendant le fetch
// 6. Retourne état error quand API et cache échouent
// 7. Cache expiré → refetch depuis API
```

**Temps estimé** : 1h

#### 1.2 - Tests Frontend : `tagsAdapter.ts`

**Fichier** : `frontend/src/utils/tagsAdapter.test.ts` ✨ NOUVEAU

```typescript
// Tests à écrire :
// 1. Transforme tagGroups en format Caracteristique[]
// 2. Gère tagGroups vide → retourne []
// 3. Inclut ungroupedTags dans un groupe "Autres"
// 4. Préserve l'ordre des tagGroups
// 5. Mappe correctement id, name, slug de chaque tag
```

**Temps estimé** : 45 min

#### 1.3 - Adapter tests existants : `Finalize.test.tsx`

**Modifications** :
- Remplacer mock `tagsApi.getAll` par mock `lacaleApi.getMeta`
- Adapter les données mockées au format API `/meta`
- Vérifier que la présélection automatique fonctionne avec les nouveaux IDs

**Temps estimé** : 1h

#### 📊 Récapitulatif Tests Phase 1

| Fichier | Tests | Temps |
|---------|-------|-------|
| `useCachedTags.test.ts` | 7 | 1h |
| `tagsAdapter.test.ts` | 5 | 45 min |
| `Finalize.test.tsx` (modif) | ~5 adaptés | 1h |
| **TOTAL** | **~17** | **2h 45min** |

---

### 🚀 PHASE 2 : BACKEND — Nettoyage

#### 2.1 - Supprimer le router tags

**Fichier à supprimer** : `backend/app/routers/tags.py`

Ce router servait à lire et parser `tags_data.json`. Avec la migration vers l'API La Cale, il n'est plus nécessaire. L'endpoint `/lacale/meta` (déjà implémenté dans `routers/lacale.py`) le remplace entièrement.

#### 2.2 - Mettre à jour `main.py`

**Fichier** : `backend/app/main.py`

Supprimer :
```python
from .routers import tags
app.include_router(tags.router, prefix="/api")
```

#### 2.3 - Mettre à jour `Dockerfile`

**Fichier** : `backend/Dockerfile`

Supprimer la ligne :
```dockerfile
COPY app/data/tags_data.json /app/data/tags_data.json
```

#### 2.4 - Supprimer les tests du router tags

Supprimer les tests liés au router tags dans `test_routers.py` ou fichier dédié s'il existe.

**Temps estimé** : 30 min

---

### 🚀 PHASE 3 : FRONTEND — Utilitaires

#### 3.1 - `tagsAdapter.ts`

**Fichier** : `frontend/src/utils/tagsAdapter.ts` ✨ NOUVEAU (~60 lignes)

```typescript
import type { LaCaleMetaResponse } from '../types';

interface AdaptedTag {
  id: string;      // ID API La Cale (pour l'upload)
  name: string;    // Nom affiché
  slug: string;    // Slug
}

interface AdaptedTagGroup {
  name: string;         // Nom du groupe (ex: "Qualité vidéo")
  tags: AdaptedTag[];   // Tags du groupe
}

/**
 * Transforme la réponse /meta en groupes de tags exploitables par Finalize
 */
export function adaptMetaToTagGroups(meta: LaCaleMetaResponse): AdaptedTagGroup[] {
  const groups: AdaptedTagGroup[] = [];
  
  // tagGroups → AdaptedTagGroup[]
  for (const tg of meta.tagGroups || []) {
    groups.push({
      name: tg.name,
      tags: (tg.tags || []).map(t => ({
        id: t.id,
        name: t.name,
        slug: t.slug,
      })),
    });
  }
  
  // ungroupedTags → groupe "Autres" (si non vide)
  if (meta.ungroupedTags?.length) {
    groups.push({
      name: "Autres",
      tags: meta.ungroupedTags.map(t => ({
        id: t.id,
        name: t.name,
        slug: t.slug,
      })),
    });
  }
  
  return groups;
}
```

**Temps estimé** : 30 min

#### 3.2 - `useCachedTags.ts`

**Fichier** : `frontend/src/hooks/useCachedTags.ts` ✨ NOUVEAU (~70 lignes)

```typescript
import { useQuery } from '@tanstack/react-query';
import { lacaleApi } from '../services/api';
import type { LaCaleMetaResponse } from '../types';

const CACHE_KEY = 'lacale_meta_cache';
const STALE_TIME = 60 * 60 * 1000; // 1 heure

function loadFromLocalStorage(): LaCaleMetaResponse | null {
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) return null;
    const parsed = JSON.parse(cached);
    // Vérifier expiration (24h pour localStorage)
    if (parsed._cachedAt && Date.now() - parsed._cachedAt > 24 * 60 * 60 * 1000) {
      localStorage.removeItem(CACHE_KEY);
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

function saveToLocalStorage(data: LaCaleMetaResponse): void {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify({
      ...data,
      _cachedAt: Date.now(),
    }));
  } catch {
    // localStorage plein ou indisponible
  }
}

export function useCachedTags() {
  return useQuery<LaCaleMetaResponse>({
    queryKey: ['lacale-meta'],
    queryFn: async () => {
      const data = await lacaleApi.getMeta();
      saveToLocalStorage(data);
      return data;
    },
    staleTime: STALE_TIME,
    placeholderData: () => loadFromLocalStorage() ?? undefined,
    retry: 1,
  });
}
```

**Temps estimé** : 45 min

---

### 🚀 PHASE 4 : FRONTEND — Finalize.tsx

#### 4.1 - Remplacer le chargement des tags

**Avant** (lignes 186-230) :
```typescript
const { data: tagsData, isLoading: isLoadingTags } = useQuery({
  queryKey: ['tags'],
  queryFn: tagsApi.getAll,
});
// ... getFilmsCaracteristiques() avec quaiprincipalcategories
```

**Après** :
```typescript
import { useCachedTags } from '../hooks/useCachedTags';
import { adaptMetaToTagGroups } from '../utils/tagsAdapter';

const { data: metaData, isLoading: isLoadingTags } = useCachedTags();
const tagGroups = metaData ? adaptMetaToTagGroups(metaData) : [];
```

#### 4.2 - Adapter le système de sélection

**Avant** : `selectedTags` contient des `tag.name` (string)  
**Après** : `selectedTags` contient des `tag.id` (string API La Cale)

Impact sur :
- `toggleTag(tag.id)` au lieu de `toggleTag(tag.name)`
- `selectedTags.includes(tag.id)` pour la mise en surbrillance
- Les tag IDs sont envoyés directement à `/lacale/upload` (champ `tag_ids`)
- La présélection automatique doit matcher par `tag.name` ou `tag.slug` puis stocker `tag.id`

#### 4.3 - Adapter la présélection automatique

La présélection automatique (basée sur MediaInfo et TMDB) doit :
1. Chercher les tags par `name` ou `slug` (ex: "1080p", "x264", "MULTi")
2. Stocker les `id` correspondants dans `selectedTags`

```typescript
const addTagIfExists = (tagName: string) => {
  for (const group of tagGroups) {
    const found = group.tags.find(
      t => t.name.toLowerCase() === tagName.toLowerCase() 
        || t.slug.toLowerCase() === tagName.toLowerCase()
    );
    if (found && !autoTags.includes(found.id)) {
      autoTags.push(found.id);
    }
  }
};
```

#### 4.4 - Adapter le rendu des tags

**Avant** :
```tsx
{getFilmsCaracteristiques().map((carac) => (
  <div key={carac.name}>
    <h4>{carac.name}</h4>
    {carac.tags.map((tag) => (
      <button onClick={() => toggleTag(tag.name)}
              className={selectedTags.includes(tag.name) ? 'selected' : ''}>
        {tag.name}
      </button>
    ))}
  </div>
))}
```

**Après** :
```tsx
{tagGroups.map((group) => (
  <div key={group.name}>
    <h4>{group.name}</h4>
    {group.tags.map((tag) => (
      <button key={tag.id}
              onClick={() => toggleTag(tag.id)}
              className={selectedTags.includes(tag.id) ? 'selected' : ''}>
        {tag.name}
      </button>
    ))}
  </div>
))}
```

**Temps estimé** : 2h

---

### 🚀 PHASE 5 : NETTOYAGE

#### 5.1 - Supprimer `tagsApi` de `api.ts`

Supprimer l'objet `tagsApi` et son import dans `Finalize.tsx`.

#### 5.2 - Supprimer les anciens types tags

Dans `types/index.ts`, supprimer les types liés à l'ancien format :
- `Caracteristique` (si plus utilisé nulle part)
- Tout type lié à `quaiprincipalcategories`

#### 5.3 - Supprimer le volume `tags_data.json` de Docker

**Fichier** : `docker-compose.yml` (ligne 12)

Supprimer :
```yaml
- ./tags_data.json:/app/data/tags_data.json:ro
```

**Fichier** : `docker-compose.dev.yml` (si existant, même suppression)

#### 5.4 - Archiver `tags_data.json`

```bash
mv tags_data.json tags_data.json.archive
```

**Temps estimé** : 30 min

---

### 🚀 PHASE 6 : DOCUMENTATION

Mettre à jour les références à `tags_data.json` dans `AGENTS.md` :
- Section "Structure du Projet" : retirer `tags_data.json`
- Section "Système de Tags" : mettre à jour la description
- Section "Paramètres" : mentionner que les tags viennent de l'API
- Section "Fichiers de Référence" : retirer `tags_data.json`
- Section "Questions ouvertes" : marquer la question tags comme résolue

**Temps estimé** : 30 min

---

### 🌳 GIT — Structure des commits

**Ordre recommandé** (7 commits) :

1. **Tests utilitaires frontend** (12 tests)
   ```
   test: ajout tests TDD tagsAdapter et useCachedTags
   ```

2. **Tests Finalize adaptés** (~5 tests modifiés)
   ```
   test: adapter mocks Finalize pour API /meta
   ```

3. **Backend nettoyage** (suppression router tags + Dockerfile)
   ```
   refactor: supprimer router tags statique (remplacé par /lacale/meta)
   ```

4. **Frontend utilitaires** (tagsAdapter + useCachedTags)
   ```
   feat: adaptateur tags API + hook cache localStorage
   ```

5. **Frontend Finalize** (migration complète)
   ```
   feat: migration tags Finalize vers API dynamique La Cale
   ```

6. **Nettoyage** (tagsApi, types, docker-compose, archive)
   ```
   chore: nettoyage tags statiques (api, types, docker, archive)
   ```

7. **Documentation**
   ```
   docs: mise à jour AGENTS.md références tags
   ```

**⚠️ IMPORTANT** : Ne jamais commit/push sans demande explicite de l'utilisateur !

---

### 📈 ESTIMATION TOTALE

| Phase | Description | Temps |
|-------|-------------|-------|
| Phase 1 | Tests TDD (~17 tests) | 2h 45min |
| Phase 2 | Backend nettoyage | 30 min |
| Phase 3 | Frontend utilitaires | 1h 15min |
| Phase 4 | Frontend Finalize | 2h |
| Phase 5 | Nettoyage | 30 min |
| Phase 6 | Documentation | 30 min |
| **TOTAL** | | **~7h 30min** |

---

### 🔄 Plan de rollback

Si la migration échoue ou si l'API La Cale est indisponible :

1. `git revert` les commits Étape 3
2. Renommer `tags_data.json.archive` → `tags_data.json`
3. Restaurer le volume Docker dans `docker-compose.yml`
4. Le router tags (`tags.py`) sera restauré par le revert Git

**Fallback permanent** : Le hook `useCachedTags` utilise localStorage comme cache de secours. Si l'API est down, les derniers tags chargés seront affichés. Seule la première utilisation (cache vide + API down) affichera une erreur.

---

### 🚨 POINTS D'ATTENTION

- **API key requise** : L'endpoint `/meta` nécessite l'API key (`X-Api-Key` header). Si l'utilisateur n'a pas configuré sa clé, les tags ne chargeront pas → afficher un message clair
- **IP restriction** : L'API La Cale a une restriction IP. Les tests unitaires doivent mocker les appels HTTP
- **Tags IDs vs Names** : Le changement de `tag.name` → `tag.id` dans `selectedTags` est un breaking change pour le store. S'assurer que le store est bien vidé/réinitialisé
- **Présélection** : La logique de présélection automatique (basée sur MediaInfo) doit chercher par `name`/`slug` mais stocker des `id`

---

### ❓ QUESTIONS OUVERTES (Étape 3)

1. **Filtrage tagGroups par catégorie** : L'API ne filtre pas les tagGroups par Films/Séries. Faut-il filtrer côté frontend ou tout afficher ?
   - **Décision actuelle** : Tout afficher (le tracker valide côté serveur)
2. **Cache localStorage expiration** : 24h est-il suffisant ?
3. **Suppression complète `tags_data.json`** : Archiver (.archive) ou supprimer définitivement ?
   - **Décision actuelle** : Archiver (renommer en .archive)