/**
 * Fallback local des tags vidéo La Cale avec leurs vrais IDs.
 *
 * Source : tags_data.json — sections Films (lignes 1624-2040) et Séries TV (lignes 2768-3173).
 * Les IDs sont identiques entre Films et Séries, sauf 2 genres exclusifs Films :
 *   - "Collections" (d5l48s1ua6hc738ejoo0)
 *   - "Téléfilm" (d5hn26pua6hc738iv6ig)
 *
 * Ce fichier sert de fallback quand l'API /meta retourne tags:null pour les groupes vidéo
 * (17 sur 25 groupes sont vides dans la réponse API actuelle).
 */
import type { LaCaleMetaResponse } from '../types';

const BOTH = ['films', 'series'];
const FILMS_ONLY = ['films'];

export const FALLBACK_META_DATA: LaCaleMetaResponse = {
  categories: [
    {
      id: 'cmjoyv2c400007ery2w2eakhy',
      name: 'Vidéo',
      slug: 'video',
      children: [
        { id: 'cmjoyv2cd00027eryreyk39gz', name: 'Films', slug: 'films', children: [] },
        { id: 'cmjoyv2dg00067ery8m6c3q8h', name: 'Séries TV', slug: 'series', children: [] },
      ],
    },
  ],
  tagGroups: [
    {
      id: 'tg_genres',
      name: 'Genres',
      slug: 'genres',
      tags: [
        { id: 'cmjudwh76000guyrus1jc9jxs', name: 'Action', slug: 'action', categories: BOTH },
        { id: 'cmjudwhrd000iuyruhm4bd82d', name: 'Animation', slug: 'animation', categories: BOTH },
        { id: 'cmjudwhi0000huyru6x3xirry', name: 'Aventure', slug: 'aventure', categories: BOTH },
        { id: 'cmjudwl30000tuyrug7nl1dih', name: 'Biopic', slug: 'biopic', categories: BOTH },
        { id: 'd5l48s1ua6hc738ejoo0', name: 'Collections', slug: 'collections', categories: FILMS_ONLY },
        { id: 'cmjudwi0v000juyrujjoqy8ya', name: 'Comédie', slug: 'com-die', categories: BOTH },
        { id: 'cmjudwld7000uuyrusigq41k6', name: 'Courts-métrages', slug: 'courts-m-trages', categories: BOTH },
        { id: 'cmjudwiay000kuyruuh6y6sux', name: 'Documentaire', slug: 'documentaire', categories: BOTH },
        { id: 'cmjudwilv000luyruldwrewad', name: 'Drame', slug: 'drame', categories: BOTH },
        { id: 'cmjudwteq001juyruql1f2o18', name: 'Émission TV', slug: '-mission-tv', categories: BOTH },
        { id: 'cmjudwiw7000muyruiwezf9u9', name: 'Fantastique', slug: 'fantastique', categories: BOTH },
        { id: 'cmjudwkto000suyruryh2tokp', name: 'Guerre', slug: 'guerre', categories: BOTH },
        { id: 'cmjudwllt000vuyruryo0oj20', name: 'Historique', slug: 'historique', categories: BOTH },
        { id: 'cmjudwj5c000nuyruu32px04l', name: 'Horreur', slug: 'horreur', categories: BOTH },
        { id: 'cmjudwjf9000ouyrud0gadn2q', name: 'Policier / Thriller', slug: 'policier-thriller', categories: BOTH },
        { id: 'cmjudwkdw000ruyruwu1f7ps7', name: 'Romance', slug: 'romance', categories: BOTH },
        { id: 'cmjudwjri000puyru2t0vy9w9', name: 'Science-fiction', slug: 'science-fiction', categories: BOTH },
        { id: 'cmjudwt42001iuyru9xod9658', name: 'Sport', slug: 'sport', categories: BOTH },
        { id: 'd5hn26pua6hc738iv6ig', name: 'Téléfilm', slug: 't-l-film', categories: FILMS_ONLY },
        { id: 'cmjudwk3e000quyrumxlv4nxg', name: 'Western', slug: 'western', categories: BOTH },
      ],
    },
    {
      id: 'tg_qualite_resolution',
      name: 'Qualité / Résolution',
      slug: 'qualit-r-solution',
      tags: [
        { id: '44d9f0e4-5ff2-4c6f-9e17-ec2e33acf448', name: '1080p (Full HD)', slug: '1080p-full-hd', categories: BOTH },
        { id: 'e42ac76f-d1b0-4ea4-a3da-f332af0f8f4c', name: '2160p (4K)', slug: '2160p-4k', categories: BOTH },
        { id: '20d145d3-db89-4996-933c-48cf51ee5b6b', name: '4320p (8K)', slug: '4320p-8k', categories: BOTH },
        { id: '86e547c3-7416-46c5-a759-fc1a5d32cc23', name: '720p (HD)', slug: '720p-hd', categories: BOTH },
        { id: 'cmjudwm65000xuyrubkb2ztkf', name: 'SD', slug: 'sd', categories: BOTH },
      ],
    },
    {
      id: 'tg_codec_video',
      name: 'Codec vidéo',
      slug: 'codec-vid-o',
      tags: [
        { id: 'cmjudwnvj0010uyrusdqdsydj', name: 'AV1', slug: 'av1', categories: BOTH },
        { id: 'cmjoyv2id000u7eryugoe1bee', name: 'AVC/H264/x264', slug: 'avc-h264-x264', categories: BOTH },
        { id: 'cmjoyv2ig000v7eryc9hf1hsa', name: 'HEVC/H265/x265', slug: 'hevc-h265-x265', categories: BOTH },
        { id: '5c9bb557-4fd7-488a-8ce7-83c26c7049f2', name: 'MPEG', slug: 'mpeg', categories: BOTH },
        { id: '168bff0e-8649-4fb4-86d9-87006c2aa511', name: 'VC-1', slug: 'vc-1', categories: BOTH },
        { id: 'f77bbe91-82c6-440d-a302-c3015edc19a8', name: 'VCC/H266/x266', slug: 'vcc-h266-x266', categories: BOTH },
        { id: '34d10b63-fcd7-4b12-91df-48cde5cb63c0', name: 'VP9', slug: 'vp9', categories: BOTH },
      ],
    },
    {
      id: 'tg_caracteristiques_video',
      name: 'Caractéristiques vidéo',
      slug: 'caract-ristiques-vid-o',
      tags: [
        { id: 'd3827daf-6d53-4d61-8e88-5a5b33ddd85f', name: '10 bits', slug: '10-bits', categories: BOTH },
        { id: 'd5eg09psup7s739bto70', name: '3D', slug: '3d', categories: BOTH },
        { id: '862f0aaf-e08d-492f-bf2d-9806c74b676a', name: 'Dolby Vision', slug: 'dolby-vision', categories: BOTH },
        { id: '4e2f5500-05f9-4f35-b273-233abc8ff991', name: 'HDR', slug: 'hdr', categories: BOTH },
        { id: 'da699e63-de34-4c75-8d65-243d8eb51151', name: 'HDR10+', slug: 'hdr10-', categories: BOTH },
        { id: '79771165-c073-490d-81e3-a408b01cfaa6', name: 'HLG', slug: 'hlg', categories: BOTH },
        { id: 'd5gh4ohsup7s73b5irt0', name: 'IMAX', slug: 'imax', categories: BOTH },
        { id: '2a3d5386-ba5f-4cce-b957-1456a6a938da', name: 'SDR', slug: 'sdr', categories: BOTH },
      ],
    },
    {
      id: 'tg_source_type',
      name: 'Source / Type',
      slug: 'source-type',
      tags: [
        { id: 'd77a8e79-0035-4df8-8cef-8311a1ea1919', name: '4KLight', slug: '4klight', categories: BOTH },
        { id: 'a063935d-adc5-4e69-af04-54f318a80771', name: 'BluRay', slug: 'bluray', categories: BOTH },
        { id: '48c926bc-8fb6-4163-99b7-c745aba4f1ed', name: 'DVDRip', slug: 'dvdrip', categories: BOTH },
        { id: 'fca2b774-3587-426c-8b7a-08e0fe51f2c6', name: 'FULL Disc', slug: 'full-disc', categories: BOTH },
        { id: 'a1c90ed0-a4b9-4444-bd8d-a4fce8dc5caf', name: 'HDLight', slug: 'hdlight', categories: BOTH },
        { id: 'f4e1b729-bc12-4957-94ee-53d10bfbf63a', name: 'REMUX', slug: 'remux', categories: BOTH },
        { id: 'f8d828b1-1d48-443f-8749-dd4af5cba373', name: 'TV', slug: 'tv', categories: BOTH },
        { id: '7bd8b291-6e18-4322-9c35-b3470c90039e', name: 'WEB-DL', slug: 'web-dl', categories: BOTH },
        { id: '86413ec8-af63-4fe2-8c88-cb56ec1b176c', name: 'WEBRip', slug: 'webrip', categories: BOTH },
      ],
    },
    {
      id: 'tg_codec_audio',
      name: 'Codec audio',
      slug: 'codec-audio',
      tags: [
        { id: 'cmjudwo5h0011uyruofwyb2cn', name: 'AAC', slug: 'aac', categories: BOTH },
        { id: 'cmjudwodw0012uyrut8jh456x', name: 'AC3', slug: 'ac3', categories: BOTH },
        { id: 'd5e5hc1sup7s73ag6eig', name: 'AC4', slug: 'ac4', categories: BOTH },
        { id: 'd5e5hnhsup7s73ecfpl0', name: 'Autres', slug: 'autres', categories: BOTH },
        { id: 'cmjudwomi0013uyruthukb2pf', name: 'DTS', slug: 'dts', categories: BOTH },
        { id: '5e8475fe-db59-4dd8-84fe-7186eaba134d', name: 'DTS-HD HR', slug: 'dts-hd-hr', categories: BOTH },
        { id: 'f87c6b8e-6edf-4dbd-b642-205d1060c0d1', name: 'DTS-HD MA', slug: 'dts-hd-ma', categories: BOTH },
        { id: 'ec308312-a650-4b00-b011-e624c8779939', name: 'DTS:X', slug: 'dts-x', categories: BOTH },
        { id: '3ab66a11-d74c-49b7-a3f9-2efc0edfefb2', name: 'E-AC3', slug: 'e-ac3', categories: BOTH },
        { id: '38ea7ff5-bd03-4b41-af5c-211792c0d1e8', name: 'E-AC3 Atmos', slug: 'e-ac3-atmos', categories: BOTH },
        { id: 'd5e6q01sup7s738q0tsg', name: 'FLAC', slug: 'flac', categories: BOTH },
        { id: 'c1f82902-ad95-4a1c-abdb-3dd8f12b1f40', name: 'HE-AAC', slug: 'he-aac', categories: BOTH },
        { id: 'd5e6q2psup7s738q0tt0', name: 'MP3', slug: 'mp3', categories: BOTH },
        { id: 'ebad8b2b-0f23-4a3a-a741-9098e61d5f46', name: 'Opus', slug: 'opus', categories: BOTH },
        { id: '4b6f7605-3aa3-411e-8bb4-fd6fcbc9c921', name: 'PCM', slug: 'pcm', categories: BOTH },
        { id: 'c45a5dbb-aad2-461c-96d2-ee4cee3f5d5b', name: 'TrueHD', slug: 'truehd', categories: BOTH },
        { id: '963a0227-d20b-4878-aa84-1deac1de4479', name: 'TrueHD Atmos', slug: 'truehd-atmos', categories: BOTH },
      ],
    },
    {
      id: 'tg_langues_audio',
      name: 'Langues audio',
      slug: 'langues-audio',
      tags: [
        { id: 'd5elgi9sup7s73emca6g', name: 'Autre Langue', slug: 'autre-langue', categories: BOTH },
        { id: 'd5eldm1sup7s7387o7ng', name: 'Chinois', slug: 'chinois', categories: BOTH },
        { id: 'd5e5kn1sup7s73b1q4pg', name: 'English', slug: 'english', categories: BOTH },
        { id: '2d45b5d1-2dfe-4de5-b0fe-e4a08132d06a', name: 'French', slug: 'french', categories: BOTH },
        { id: 'd5e5jh1sup7s73ecfppg', name: 'Italian', slug: 'italian', categories: BOTH },
        { id: 'd5e5jchsup7s73ecfpog', name: 'Japanese', slug: 'japanese', categories: BOTH },
        { id: 'd5e5jepsup7s73f6hn9g', name: 'Korean', slug: 'korean', categories: BOTH },
        { id: 'cmjoyv2i0000q7eryz0dnb7f9', name: 'MULTI', slug: 'multi', categories: BOTH },
        { id: 'd5hb34pua6hc739gjva0', name: 'Sans Dialogue', slug: 'sans-dialogue', categories: BOTH },
        { id: 'd5e5mhhsup7s73cq0sr0', name: 'Spanish', slug: 'spanish', categories: BOTH },
        { id: '5cc1e14d-b23a-42c5-956e-3ad9e1529b3c', name: 'VFF', slug: 'vff', categories: BOTH },
        { id: 'b4661137-ed7a-4742-8ebc-40fcb6fa8f8d', name: 'VFQ', slug: 'vfq', categories: BOTH },
      ],
    },
    {
      id: 'tg_sous_titres',
      name: 'Sous-titres',
      slug: 'sous-titres',
      tags: [
        { id: 'd5elg3psup7s73emvf3g', name: 'Autres sous-titres', slug: 'autres-sous-titres', categories: BOTH },
        { id: 'd5e6lu9sup7s73a9mimg', name: 'ENG', slug: 'eng', categories: BOTH },
        { id: 'cmjudwg9q000euyruscojd2q4', name: 'FR', slug: 'fr', categories: BOTH },
        { id: 'd5elf41sup7s73emc85g', name: 'VFF Sous-Titres', slug: 'vff-sous-titres', categories: BOTH },
        { id: 'd5elilhsup7s73avoesg', name: 'VFQ Sous-Titres', slug: 'vfq-sous-titres', categories: BOTH },
      ],
    },
    {
      id: 'tg_extension',
      name: 'Extension',
      slug: 'extension',
      tags: [
        { id: 'd5fuf51sup7s73bbcmq0', name: 'Autres Extensions', slug: 'autres-extensions', categories: BOTH },
        { id: 'd5fueopsup7s73cg5qo0', name: 'AVI', slug: 'avi', categories: BOTH },
        { id: 'd5fuevpsup7s739du1l0', name: 'ISO', slug: 'iso', categories: BOTH },
        { id: 'd5fuer9sup7s73eq24s0', name: 'MKV', slug: 'mkv', categories: BOTH },
        { id: 'd5fuelpsup7s73b9ntu0', name: 'MP4', slug: 'mp4', categories: BOTH },
      ],
    },
  ],
  ungroupedTags: [],
};
