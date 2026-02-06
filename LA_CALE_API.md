Accès rapide
Base URL: https://la-cale.space
---

Toutes les requêtes doivent inclure une Clé API valide. Générez-en une dans vos paramètres.

GET /api/external

Exemple: /api/external?apikey=VOTRE_CLE_API&q=One%20Piece&cat=films

GET /api/external/meta

Catégories, sous-catégories et tags: /api/external/meta?apikey=VOTRE_CLE_API

POST /api/external/upload

Multipart (Header X-Api-Key ou Query apikey): title, categoryId, file, tags[], nfoFile

GET /api/torrents/download/<infoHash>

Ajoutez ?apikey=VOTRE_CLE_API pour récupérer le fichier .torrent sans être connecté.

Authentification
Toutes les requêtes doivent inclure une Clé API. Vous pouvez gérer vos clés dans les paramètres du compte.

Méthodes acceptées :
Header: X-Api-Key: VOTRE_CLE (Recommandé pour les scripts)
Query: ?apikey=VOTRE_CLE (Recommandé pour Prowlarr/Jackett)

GET /api/external?apikey=VOTRE_CLE_API
Points d'Entrée
Recherche & Indexation
Compatible avec les formats JSON standards d'indexeurs (Prowlarr, Jackett, scripts maison).

GET /api/external

apikey (ou Header X-Api-Key) : Votre clé secrète.
q (optionnel) : Terme de recherche.
tmdbId (optionnel) : ID TMDB exact (ex:12345).
cat (optionnel) : Slug de la catégorie (ex:films). Vous pouvez répéter le paramètre autant de fois que vous voulez pour filtrer sur plusieurs slugs à la fois (&cat=films&cat=series).
Limites: q max 200 caracteres, cat max 64 caracteres, tmdbId max 64 caracteres.
Résultats: 50 items max, triés par date décroissante.
Statut: retourne uniquement les torrents approuvés.
Réponse JSON

title, guid, size
pubDate, link, category
seeders, leechers, infoHash
[ { "title": "One.Piece.S01E01.1080p", "guid": "ckx9f3p5x0000abcd1234", "size": 2147483648, "pubDate": "2025-01-12T10:00:00.000Z", "link": "https://la-cale.space/api/torrents/download/<infoHash>", "category": "Séries TV", "seeders": 42, "leechers": 3, "infoHash": "abcdef..." } ]
Cache serveur: ~30s par combinaison passkey + query + catégorie.

Schéma des champs

title: string
guid: string (ID interne)
size: number (bytes)
pubDate: string (ISO 8601)
link: string (URL download)
category: string (libellé)
seeders: number
leechers: number
infoHash: string (hex)
Notes de recherche

q est normalisé (minuscules, accents supprimés).
cat attend le slug d'une catégorie (ex: films, series).
Pour lister les slugs et IDs, utilisez /api/external/meta.
Métadonnées (catégories & tags)
Permet de récupérer toutes les informations nécessaires pour remplir un upload (catégories, sous-catégories, tags, groupes).

GET /api/external/meta

passkey (requis)
Réponse: categories, tagGroups, ungroupedTags
Chaque catégorie/tag expose son slug (voir categories[].slug et tagGroups[].tags[].slug) : utilisez-le dans cat.
Utilisation

categoryId vient de categories[].id ou categories[].children[].id.
tags attend des IDs (champ répété) depuis tagGroups[].tags[].id.
ungroupedTags contient les tags sans groupe.
Exemple de réponse (extrait)

{ "categories": [ { "id": "cat_video", "name": "Vidéo", "slug": "video", "children": [ { "id": "cat_films", "name": "Films", "slug": "films" }, { "id": "cat_series", "name": "Séries TV", "slug": "series" } ] } ], "tagGroups": [ { "id": "tg_video_quality", "name": "Qualité vidéo", "tags": [ { "id": "tag_1080p", "name": "1080p", "slug": "1080p" } ] } ], "ungroupedTags": [] }
Schéma des champs

categories[]: { id, name, slug, icon?, parentId?, children[] }
tagGroups[]: { id, name, slug, order, tags[] }
ungroupedTags[]: { id, name, slug }
Upload (API)
Permet de décharger une cargaison directement depuis vos scripts.

POST /api/external/upload

Content-Type: multipart/form-data

Champs requis

passkey
title
categoryId
file (.torrent)
Champs optionnels

description
tmdbId, tmdbType (MOVIE/TV)
coverUrl (URL directe de l'affiche)
tags (répété, IDs de tags)
nfoFile
coverUrl accepte une URL publique (https). Si tmdbId est fourni, il peut être remplacé par l'affiche TMDB.

Limites: rate limiting strict (30/min). Renvoie 429 en cas d'abus.

Important: le torrent doit contenir le source flag lacale. Sinon le client devra retélécharger le torrent depuis le site.

Réponse JSON

success, id, slug
link
{ "success": true, "id": "ckx9f3p5x0000abcd1234", "slug": "ma-cargaison-abc123", "link": "https://la-cale.space/torrents/ma-cargaison-abc123" }
Schéma des champs (upload)

passkey: string (requis)
title: string (requis)
categoryId: string (requis, ID catégorie)
file: fichier .torrent (requis)
tags: string[] (IDs, répété)
description: string
tmdbId: string
tmdbType: "MOVIE" | "TV"
coverUrl: string (URL)
nfoFile: fichier .nfo
Tags: comment les envoyer

Envoyez plusieurs fois le champ tags:tags=TAG_ID_1, tags=TAG_ID_2.
Les tags attendent des IDs (pas des slugs).
Récupérez les IDs via /api/external/meta.
Exemples de scripts
cURL
Python
Node.js
PHP
Recherche
const axios = require("axios");

async function checkTheHolds() {
  try {
    const res = await axios.get("https://la-cale.space/api/external", {
      headers: { "X-Api-Key": "VOTRE_CLE_API" },
      params: {
        q: "Pirates",
        tmdbId: "12345",
        cat: "films",
      }
    });
    console.log("Butin trouvé:", res.data.length);
  } catch (err) {
    console.error("Mutinerie sur le réseau!", err.message);
  }
}

checkTheHolds();
Métadonnées
const axios = require("axios");

async function getMeta() {
  const res = await axios.get("https://la-cale.space/api/external/meta", {
    headers: { "X-Api-Key": "VOTRE_CLE_API" }
  });
  console.log(res.data);
}

getMeta();
Upload
const axios = require("axios");
const FormData = require("form-data");
const fs = require("fs");

async function uploadCargaison() {
  const form = new FormData();
  // form.append("passkey", "VOTRE_PASSKEY"); // Not needed in body if using header
  form.append("title", "Ma Cargaison");
  form.append("categoryId", "ID_DU_QUAI");
  form.append("tags", "TAG_ID_1");
  form.append("tags", "TAG_ID_2");
  form.append("coverUrl", "https://example.com/cover.jpg");
  form.append("file", fs.createReadStream("./film.torrent"));

  try {
    const res = await axios.post("https://la-cale.space/api/external/upload", form, {
      headers: { 
        ...form.getHeaders(),
        "X-Api-Key": "VOTRE_CLE_API"
      }
    });
    console.log("Succès !", res.data);
  } catch (err) {
    console.error("Échec", err.response?.data || err.message);
  }
}

uploadCargaison();
Erreurs courantes
400 : requête trop longue, catégorie invalide, champs manquants, torrent illisible.
401 : clé API manquante.
403 : clé API invalide.
409 : torrent déjà existant (même InfoHash).
429 : rate limit dépassé (IP ou clé API).
500 : erreur serveur (réessayer plus tard).
Notes & Bonnes pratiques
Trouver categoryId et tags (en 3 étapes)

Appeler /api/external/meta?apikey=...
Repérer la catégorie souhaitée dans categories[].children[] et copier son id
Choisir des tags depuis tagGroups[].tags[] et envoyer leurs id dans le champ répété tags