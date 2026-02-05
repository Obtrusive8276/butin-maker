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
