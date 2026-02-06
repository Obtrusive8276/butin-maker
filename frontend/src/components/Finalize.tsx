import { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Download, Copy, Check, ExternalLink, FileText, File, Tags, Eye, X, Play, Loader2 } from 'lucide-react';
import DOMPurify from 'dompurify';
import { useAppStore } from '../stores/appStore';
import { torrentApi, mediainfoApi, tagsApi, presentationApi } from '../services/api';
import { useClipboard } from '../hooks/useClipboard';
import { getResolutionFromWidth } from '../utils/format';
import type { Caracteristique } from '../types';

export default function Finalize() {
  const { 
    torrentResult, 
    nfoPath, 
    generatedBBCode,
    setGeneratedBBCode,
    setPresentationData,
    selectedTags,
    toggleTag,
    setSelectedTags,
    settings,
    selectedFiles,
    contentType,
    mediaInfo,
    releaseName,
    tmdbInfo
  } = useAppStore();
  
  const { copy: copyBBCode, copied: copiedBBCode } = useClipboard();
  const [hasAutoSelected, setHasAutoSelected] = useState(false);
  const [showNfoPreview, setShowNfoPreview] = useState(false);
  const [showBBCodePreview, setShowBBCodePreview] = useState(false);
  const [nfoContent, setNfoContent] = useState<string | null>(null);
  const [seedingStatus, setSeedingStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [seedingMessage, setSeedingMessage] = useState('');

  // Fonction de sanitization sécurisée avec DOMPurify
  const sanitizeHtml = (html: string): string => {
    // Ajouter un hook pour filtrer les attributs dangereux
    DOMPurify.addHook('afterSanitizeAttributes', (node) => {
      // Filtrer les src avec data:, blob:, etc.
      if (node.hasAttribute('src')) {
        const src = node.getAttribute('src') || '';
        if (!src.match(/^https?:\/\//i) && !src.match(/^ftp:\/\//i)) {
          node.removeAttribute('src');
        }
      }
      // Filtrer les styles avec url() malveillants
      if (node.hasAttribute('style')) {
        const style = node.getAttribute('style') || '';
        if (style.includes('url(') && !style.match(/url\s*\(\s*['"]?https?:\/\//i)) {
          // Retirer les url() qui ne sont pas HTTP(S)
          const cleanStyle = style.replace(/url\s*\([^)]*\)/gi, '');
          node.setAttribute('style', cleanStyle);
        }
      }
    });

    const sanitized = DOMPurify.sanitize(html, {
      ALLOWED_TAGS: ['div', 'span', 'strong', 'em', 'u', 's', 'a', 'img', 'blockquote', 'pre', 'code', 'ul', 'li', 'hr', 'br'],
      ALLOWED_ATTR: ['style', 'href', 'target', 'rel', 'src', 'width', 'height'],
      ALLOWED_URI_REGEXP: /^(?:(?:https?|ftp):\/\/)/i,
    });

    // Nettoyer les hooks pour éviter les effets de bord
    DOMPurify.removeAllHooks();

    return sanitized;
  };

  // Convertir BBCode en HTML pour l'aperçu
  const bbcodeToHtml = (bbcode: string): string => {
    let html = bbcode;
    
    // Échapper le HTML existant
    html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    // [center]...[/center]
    html = html.replace(/\[center\](.*?)\[\/center\]/gis, '<div style="text-align: center;">$1</div>');
    
    // [b]...[/b]
    html = html.replace(/\[b\](.*?)\[\/b\]/gis, '<strong>$1</strong>');
    
    // [i]...[/i]
    html = html.replace(/\[i\](.*?)\[\/i\]/gis, '<em>$1</em>');
    
    // [u]...[/u]
    html = html.replace(/\[u\](.*?)\[\/u\]/gis, '<u>$1</u>');
    
    // [s]...[/s]
    html = html.replace(/\[s\](.*?)\[\/s\]/gis, '<s>$1</s>');
    
    // [color=...]...[/color]
    html = html.replace(/\[color=([^\]]+)\](.*?)\[\/color\]/gis, '<span style="color: $1;">$2</span>');
    
    // [size=...]...[/size]
    html = html.replace(/\[size=([^\]]+)\](.*?)\[\/size\]/gis, '<span style="font-size: $1;">$2</span>');
    
    // [url=...]...[/url]
    html = html.replace(/\[url=([^\]]+)\](.*?)\[\/url\]/gis, (_match, url: string, text: string) => {
      const safeUrl = /^(https?:\/\/|\/\/)/.test(url) ? url : '#';
      return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; text-decoration: underline;">${text}</a>`;
    });
    
    // [url]...[/url]
    html = html.replace(/\[url\](.*?)\[\/url\]/gis, (_match, url: string) => {
      const safeUrl = /^(https?:\/\/|\/\/)/.test(url) ? url : '#';
      return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; text-decoration: underline;">${safeUrl === '#' ? url : safeUrl}</a>`;
    });
    
    // [img]...[/img]
    html = html.replace(/\[img\](.*?)\[\/img\]/gis, (_match, url: string) => {
      const safeUrl = /^(https?:\/\/|\/\/)/.test(url) ? url : '';
      return safeUrl ? `<img src="${safeUrl}" style="max-width: 300px; height: auto; display: block; margin: 0 auto;" />` : '';
    });
    
    // [img=WxH]...[/img]
    html = html.replace(/\[img=(\d+)x(\d+)\](.*?)\[\/img\]/gis, (_match, w: string, h: string, url: string) => {
      const safeUrl = /^(https?:\/\/|\/\/)/.test(url) ? url : '';
      return safeUrl ? `<img src="${safeUrl}" width="${w}" height="${h}" style="max-width: 300px; height: auto; display: block; margin: 0 auto;" />` : '';
    });
    
    // [quote]...[/quote]
    html = html.replace(/\[quote\](.*?)\[\/quote\]/gis, '<blockquote style="border-left: 3px solid #6b7280; padding-left: 1rem; margin: 0.5rem 0; color: #9ca3af;">$1</blockquote>');
    
    // [code]...[/code]
    html = html.replace(/\[code\](.*?)\[\/code\]/gis, '<pre style="background: #1f2937; padding: 0.5rem; border-radius: 4px; overflow-x: auto;"><code>$1</code></pre>');
    
    // [list]...[/list] et [*]
    html = html.replace(/\[list\](.*?)\[\/list\]/gis, '<ul style="list-style: disc; padding-left: 1.5rem;">$1</ul>');
    html = html.replace(/\[\*\]/g, '<li>');
    
    // [hr]
    html = html.replace(/\[hr\]/gi, '<hr style="border: none; border-top: 1px solid #4b5563; margin: 1rem 0;" />');
    
    // Sauts de ligne
    html = html.replace(/\n/g, '<br />');
    
    return html;
  };

  // Mutation pour générer la présentation
  const generatePresentationMutation = useMutation({
    mutationFn: presentationApi.generate,
    onSuccess: (data) => {
      if (data.bbcode && data.bbcode.trim() !== '') {
        setGeneratedBBCode(data.bbcode);
      } else {
        console.error('BBCode vide reçu du serveur');
      }
    },
    onError: (error) => {
      console.error('Erreur lors de la génération de la présentation:', error);
    },
  });



  // Générer automatiquement la présentation si elle n'existe pas
  useEffect(() => {
    if (!generatedBBCode && tmdbInfo) {
      // Préparer les données de présentation depuis TMDB et MediaInfo
      const data = {
        title: tmdbInfo.title,
        poster_url: tmdbInfo.poster_path || '',
        rating: tmdbInfo.vote_average.toString(),
        genre: tmdbInfo.genres,
        synopsis: tmdbInfo.overview,
        quality: getResolutionFromWidth(mediaInfo?.video_tracks?.[0]?.width),
        format: mediaInfo?.container || '',
        video_codec: mediaInfo?.video_tracks?.[0]?.codec || '',
        audio_codec: mediaInfo?.audio_tracks?.[0]?.codec || '',
        languages: mediaInfo?.audio_tracks?.map(t => t.language).filter(Boolean).join(', ') || '',
        subtitles: mediaInfo?.subtitle_tracks?.map(t => t.language).filter(Boolean).join(', ') || 'Aucun',
        size: selectedFiles[0]?.size ? `${(selectedFiles[0].size / (1024 * 1024 * 1024)).toFixed(2)} GB` : ''
      };
      setPresentationData(data);
      generatePresentationMutation.mutate(data);
    }
  }, [tmdbInfo, mediaInfo, generatedBBCode]);

  // Charger les tags
  const { data: tagsData } = useQuery({
    queryKey: ['tags'],
    queryFn: tagsApi.getAll,
  });

  // Collecter tous les noms de tags existants
  const getAllTagNames = (): Set<string> => {
    const tagNames = new Set<string>();
    if (!tagsData?.quaiprincipalcategories) return tagNames;
    
    for (const category of tagsData.quaiprincipalcategories) {
      if (category.caracteristiques) {
        for (const carac of category.caracteristiques) {
          for (const tag of carac.tags || []) {
            tagNames.add(tag.name);
          }
        }
      }
      for (const subCat of category.emplacementsouscategorie || []) {
        for (const carac of subCat.caracteristiques || []) {
          for (const tag of carac.tags || []) {
            tagNames.add(tag.name);
          }
        }
      }
    }
    return tagNames;
  };

  // Récupérer les caractéristiques de la catégorie Films ou Séries
  const getFilmsCaracteristiques = (): Caracteristique[] => {
    if (!tagsData?.quaiprincipalcategories) return [];
    
    const videoCategory = tagsData.quaiprincipalcategories.find(
      (c: { slug: string }) => c.slug === 'video'
    );
    if (!videoCategory) return [];
    
    const targetSlug = contentType === 'movie' ? 'films' : 'series';
    const subCategory = videoCategory.emplacementsouscategorie?.find(
      (s: { slug: string }) => s.slug === targetSlug
    );
    
    return subCategory?.caracteristiques || [];
  };

  // Présélection automatique des tags
  useEffect(() => {
    if (!tagsData || hasAutoSelected || selectedTags.length > 0) return;
    
    const existingTags = getAllTagNames();
    const autoTags: string[] = [];
    
    const addTagIfExists = (tagName: string) => {
      if (existingTags.has(tagName) && !autoTags.includes(tagName)) {
        autoTags.push(tagName);
      }
    };
    
    // Source depuis le nom de release
    const releaseNameUpper = releaseName?.toUpperCase() || '';
    if (releaseNameUpper.includes('WEB-DL') || releaseNameUpper.includes('WEBDL')) {
      addTagIfExists('WEB-DL');
    } else if (releaseNameUpper.includes('WEBRIP')) {
      addTagIfExists('WEBRip');
    } else if (releaseNameUpper.includes('BLURAY') || releaseNameUpper.includes('BLU-RAY')) {
      addTagIfExists('BluRay');
    } else if (releaseNameUpper.includes('DVDRIP')) {
      addTagIfExists('DVDRip');
    } else if (releaseNameUpper.includes('HDTV')) {
      addTagIfExists('HDTV');
    } else if (releaseNameUpper.includes('REMUX')) {
      addTagIfExists('REMUX');
    }
    
    // Genre depuis TMDB
    if (tmdbInfo?.genres) {
      const genres = tmdbInfo.genres.split(',').map((g: string) => g.trim());
      for (const genre of genres) {
        addTagIfExists(genre);
        const capitalizedGenre = genre.charAt(0).toUpperCase() + genre.slice(1).toLowerCase();
        addTagIfExists(capitalizedGenre);
      }
    }
    
    // Codec vidéo
    if (mediaInfo) {
      const videoTrack = mediaInfo.video_tracks?.[0];
      const videoCodec = videoTrack?.codec?.toLowerCase() || '';
      if (videoCodec.includes('hevc') || videoCodec.includes('h265') || videoCodec.includes('x265')) {
        addTagIfExists('HEVC/H265/x265');
      } else if (videoCodec.includes('avc') || videoCodec.includes('h264') || videoCodec.includes('x264')) {
        addTagIfExists('AVC/H264/x264');
      } else if (videoCodec.includes('av1')) {
        addTagIfExists('AV1');
      }
      
      // Codec audio
      const audioTrack = mediaInfo.audio_tracks?.[0];
      const audioCodec = audioTrack?.codec?.toLowerCase() || '';
      if (audioCodec.includes('truehd')) {
        addTagIfExists('TrueHD Atmos');
        addTagIfExists('TrueHD');
      } else if (audioCodec.includes('dts-hd')) {
        addTagIfExists('DTS-HD MA');
      } else if (audioCodec.includes('dts')) {
        addTagIfExists('DTS');
      } else if (audioCodec.includes('e-ac-3') || audioCodec.includes('eac3')) {
        addTagIfExists('E-AC3 Atmos');
        addTagIfExists('E-AC3');
      } else if (audioCodec.includes('ac3') || audioCodec.includes('ac-3')) {
        addTagIfExists('AC3');
      } else if (audioCodec.includes('aac')) {
        addTagIfExists('AAC');
      }
      
      // Résolution - utiliser la largeur pour les films scope (ex: 1920x816 = 1080p)
      const width = videoTrack?.width || 0;
      if (width >= 3840) {
        addTagIfExists('2160p (4K UHD)');
      } else if (width >= 1920) {
        addTagIfExists('1080p (Full HD)');
      } else if (width >= 1280) {
        addTagIfExists('720p (HD)');
      }
      
      // Extension
      const fileName = mediaInfo.file_name?.toLowerCase() || '';
      if (fileName.endsWith('.mkv')) {
        addTagIfExists('MKV');
      } else if (fileName.endsWith('.mp4')) {
        addTagIfExists('MP4');
      }
      
      // Langues
      const audioTracks = mediaInfo.audio_tracks || [];
      if (audioTracks.length > 1) {
        addTagIfExists('MULTI');
      }
      if (audioTracks.some(t => t.language?.toLowerCase().includes('fr'))) {
        addTagIfExists('French');
      }
      if (audioTracks.some(t => t.language?.toLowerCase().includes('en'))) {
        addTagIfExists('English');
      }
    }
    
    if (autoTags.length > 0) {
      setSelectedTags(autoTags);
    }
    setHasAutoSelected(true);
  }, [tagsData, mediaInfo, releaseName, tmdbInfo, hasAutoSelected, selectedTags.length, setSelectedTags]);

  const filmsCaracteristiques = getFilmsCaracteristiques();

  const handleDownloadTorrent = () => {
    if (torrentResult?.torrent_name) {
      const url = torrentApi.downloadTorrent(`${torrentResult.torrent_name}.torrent`);
      window.open(url, '_blank');
    }
  };

  const handleDownloadNfo = () => {
    if (nfoPath) {
      const filename = nfoPath.split(/[/\\]/).pop() || '';
      const url = mediainfoApi.downloadNfo(filename);
      window.open(url, '_blank');
    }
  };

  const handleCopyBBCode = () => {
    copyBBCode(generatedBBCode);
  };

  const handleGoToUpload = () => {
    const uploadUrl = settings?.tracker.upload_url;
    if (uploadUrl) {
      window.open(uploadUrl, '_blank');
    }
  };

  const handleShowNfoPreview = async () => {
    if (nfoPath) {
      try {
        const filename = nfoPath.split(/[/\\]/).pop() || '';
        const response = await fetch(mediainfoApi.downloadNfo(filename));
        const text = await response.text();
        setNfoContent(text);
        setShowNfoPreview(true);
      } catch (error) {
        console.error('Erreur chargement NFO:', error);
      }
    }
  };

  const handleStartSeeding = async () => {
    if (!torrentResult?.torrent_path || !selectedFiles[0]?.path) return;
    
    setSeedingStatus('loading');
    try {
      const result = await torrentApi.addForSeeding(
        torrentResult.torrent_path,
        selectedFiles[0].path
      );
      if (result.success) {
        setSeedingStatus('success');
        setSeedingMessage(result.message);
      } else {
        setSeedingStatus('error');
        setSeedingMessage(result.message);
      }
    } catch (error) {
      setSeedingStatus('error');
      setSeedingMessage('Erreur de connexion à qBittorrent');
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-lg font-semibold mb-6">Finalisation de l'Upload</h2>

      <div className="space-y-4">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="font-medium mb-4 flex items-center gap-2">
            <File className="w-5 h-5 text-primary-500" />
            Fichier Torrent
          </h3>
          {torrentResult?.success ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-sm">
                  <p><span className="text-gray-400">Nom:</span> {torrentResult.torrent_name}</p>
                  <p className="text-xs text-gray-500 mt-1">Hash: {torrentResult.info_hash}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleStartSeeding}
                    disabled={seedingStatus === 'loading' || seedingStatus === 'success'}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 disabled:bg-green-800 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
                  >
                    {seedingStatus === 'loading' ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : seedingStatus === 'success' ? (
                      <Check className="w-4 h-4" />
                    ) : (
                      <Play className="w-4 h-4" />
                    )}
                    {seedingStatus === 'success' ? 'Seed lancé' : 'Lancer le seed'}
                  </button>
                  <button
                    onClick={handleDownloadTorrent}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-gray-900 rounded-lg font-medium hover:bg-primary-400 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Télécharger
                  </button>
                </div>
              </div>
              {seedingStatus === 'error' && (
                <p className="text-sm text-red-400">{seedingMessage}</p>
              )}
              {seedingStatus === 'success' && (
                <p className="text-sm text-green-400">{seedingMessage}</p>
              )}
            </div>
          ) : (
            <p className="text-gray-500">Aucun torrent créé</p>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="font-medium mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-400" />
            Fichier NFO
          </h3>
          {nfoPath ? (
            <div className="flex items-center justify-between">
              <p className="text-sm truncate flex-1 mr-4">{nfoPath.split(/[/\\]/).pop()}</p>
              <div className="flex gap-2">
                <button
                  onClick={handleShowNfoPreview}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium transition-colors"
                >
                  <Eye className="w-4 h-4" />
                  Aperçu
                </button>
                <button
                  onClick={handleDownloadNfo}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Télécharger
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <p className="text-gray-500">NFO non généré</p>
              <span className="text-xs text-gray-500">Optionnel</span>
            </div>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="font-medium mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-green-400" />
            Présentation BBCode
            <div className="ml-auto flex gap-2">
              <button
                onClick={() => setShowBBCodePreview(!showBBCodePreview)}
                className={`flex items-center gap-1 px-3 py-1.5 rounded text-sm ${
                  showBBCodePreview ? 'bg-primary-500 text-gray-900' : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                <Eye className="w-4 h-4" />
                {showBBCodePreview ? 'Éditer' : 'Aperçu'}
              </button>
              <button
                onClick={handleCopyBBCode}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-green-600 hover:bg-green-500 rounded"
              >
                {copiedBBCode ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copiedBBCode ? 'Copié!' : 'Copier'}
              </button>
            </div>
          </h3>
          {generatedBBCode ? (
            showBBCodePreview ? (
              <div 
                className="bg-gray-900 p-4 rounded max-h-96 overflow-auto prose prose-invert prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: sanitizeHtml(bbcodeToHtml(generatedBBCode)) }}
              />
            ) : (
              <textarea
                value={generatedBBCode}
                onChange={(e) => setGeneratedBBCode(e.target.value)}
                className="w-full h-96 bg-gray-900 border border-gray-700 rounded p-3 text-sm font-mono focus:outline-none focus:border-primary-500 resize-none"
                placeholder="BBCode de la présentation..."
              />
            )
          ) : (
            <p className="text-gray-500">Aucune présentation générée</p>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="font-medium mb-4 flex items-center gap-2">
            <Tags className="w-5 h-5 text-purple-400" />
            Tags à sélectionner sur La Cale
          </h3>
          {filmsCaracteristiques.length > 0 ? (
            <div className="space-y-4 max-h-64 overflow-y-auto">
              {filmsCaracteristiques.map((carac: Caracteristique) => (
                <div key={carac.slug}>
                  <h4 className="text-xs text-gray-400 uppercase mb-2">{carac.name}</h4>
                  <div className="flex flex-wrap gap-2">
                    {carac.tags.map((tag) => (
                      <button
                        key={tag.name}
                        onClick={() => toggleTag(tag.name)}
                        className={`px-2 py-1 rounded text-sm transition-colors ${
                          selectedTags.includes(tag.name)
                            ? 'bg-purple-500 text-white'
                            : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                        }`}
                      >
                        {selectedTags.includes(tag.name) && (
                          <Check className="w-3 h-3 inline mr-1" />
                        )}
                        {tag.name}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">Chargement des tags...</p>
          )}
        </div>

        <div className="bg-gradient-to-r from-primary-500/20 to-primary-600/20 border border-primary-500/30 rounded-lg p-6">
          <h3 className="font-medium mb-4 text-primary-500">Prêt pour l'upload!</h3>
          <p className="text-sm text-gray-300 mb-4">
            Tous les éléments sont prêts. Cliquez sur le bouton ci-dessous pour ouvrir la page d'upload de La Cale.
          </p>
          <button
            onClick={handleGoToUpload}
            disabled={!settings?.tracker.upload_url}
            className="flex items-center gap-2 px-6 py-3 bg-primary-500 text-gray-900 rounded-lg font-bold hover:bg-primary-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ExternalLink className="w-5 h-5" />
            Ouvrir La Cale - Upload
          </button>
          {!settings?.tracker.upload_url && (
            <p className="text-xs text-yellow-500 mt-2">
              Configurez l'URL d'upload dans les paramètres
            </p>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="font-medium mb-3">Récapitulatif</h3>
          <ul className="text-sm space-y-2 text-gray-400">
            <li>
              <span className="text-gray-500">Source:</span>{' '}
              {selectedFiles.length > 0 ? selectedFiles[0].name : 'N/A'}
            </li>
            <li>
              <span className="text-gray-500">Torrent:</span>{' '}
              {torrentResult?.success ? '✓ Créé' : '✗ Non créé'}
            </li>
            <li>
              <span className="text-gray-500">NFO:</span>{' '}
              {nfoPath ? '✓ Généré' : '○ Non généré'}
            </li>
            <li>
              <span className="text-gray-500">Présentation:</span>{' '}
              {generatedBBCode ? '✓ Prête' : '✗ Non générée'}
            </li>
            <li>
              <span className="text-gray-500">Tags:</span>{' '}
              {selectedTags.length} sélectionnés
            </li>
          </ul>
        </div>
      </div>

      {/* Modal Aperçu NFO */}
      {showNfoPreview && nfoContent && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <h3 className="font-semibold">Aperçu NFO</h3>
              <button
                onClick={() => setShowNfoPreview(false)}
                className="p-1 hover:bg-gray-700 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <pre className="p-4 overflow-auto flex-1 text-xs font-mono whitespace-pre">
              {nfoContent}
            </pre>
          </div>
        </div>
      )}

      {/* Modal Aperçu Présentation BBCode */}
      {showBBCodePreview && generatedBBCode && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-lg max-w-4xl w-full max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <h3 className="font-semibold">Aperçu Présentation</h3>
              <button
                onClick={() => setShowBBCodePreview(false)}
                className="p-1 hover:bg-gray-700 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div 
              className="p-6 overflow-auto flex-1 text-sm leading-relaxed"
              dangerouslySetInnerHTML={{ __html: sanitizeHtml(bbcodeToHtml(generatedBBCode)) }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
