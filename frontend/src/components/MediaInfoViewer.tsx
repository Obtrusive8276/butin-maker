import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, ArrowLeft, Loader2, Check, Copy, FolderOpen, AlertCircle } from 'lucide-react';
import { mediainfoApi, filesApi, tmdbApi } from '../services/api';
import { useAppStore } from '../stores/appStore';
import { formatSize, formatDuration, getResolutionFromWidth } from '../utils/format';
import { useClipboard } from '../hooks/useClipboard';

export default function MediaInfoViewer() {
  const { 
    selectedFiles, 
    setMediaInfo, 
    setCurrentStep, 
    setPresentationData,
    setSeriesInfo,
    setContentType,
    setMediaInfoFilePath
  } = useAppStore();
  const [showRaw, setShowRaw] = useState(false);
  const { copy: copyRawInfo, copied } = useClipboard();
  const [videoFileForAnalysis, setVideoFileForAnalysis] = useState<string | null>(null);

  const selectedItem = selectedFiles[0];
  const isDirectory = selectedItem?.is_dir || false;

  // Pour les dossiers, trouver le premier fichier vidéo
  const { data: firstVideoData, isLoading: isLoadingFirstVideo } = useQuery({
    queryKey: ['first-video', selectedItem?.path],
    queryFn: () => filesApi.getFirstVideo(selectedItem?.path || ''),
    enabled: !!selectedItem?.path && isDirectory,
  });

  // Détecter les infos de série depuis le nom
  const { data: episodeInfo } = useQuery({
    queryKey: ['episode-info', selectedItem?.name],
    queryFn: () => tmdbApi.detectEpisode(selectedItem?.name || ''),
    enabled: !!selectedItem?.name,
  });

  // Déterminer le fichier à analyser
  useEffect(() => {
    if (isDirectory && firstVideoData && !firstVideoData.error) {
      setVideoFileForAnalysis(firstVideoData.path);
      setMediaInfoFilePath(firstVideoData.path);
    } else if (!isDirectory && selectedItem?.path) {
      setVideoFileForAnalysis(selectedItem.path);
      setMediaInfoFilePath(selectedItem.path);
    }
  }, [isDirectory, firstVideoData, selectedItem, setMediaInfoFilePath]);

  // Mettre à jour les infos de série
  useEffect(() => {
    if (episodeInfo) {
      if (episodeInfo.is_series) {
        setContentType('tv');
        setSeriesInfo({
          season: episodeInfo.season,
          episode: episodeInfo.episode,
          isCompleteSeason: episodeInfo.is_complete_season
        });
      } else {
        setContentType('movie');
      }
    }
  }, [episodeInfo, setContentType, setSeriesInfo]);

  const filePath = videoFileForAnalysis || '';

  const { data: mediaInfo, isLoading } = useQuery({
    queryKey: ['mediainfo', filePath],
    queryFn: () => mediainfoApi.analyze(filePath),
    enabled: !!filePath,
  });

  const { data: rawInfo } = useQuery({
    queryKey: ['mediainfo-raw', filePath],
    queryFn: () => mediainfoApi.getRaw(filePath),
    enabled: !!filePath && showRaw,
  });

  useEffect(() => {
    if (mediaInfo) {
      setMediaInfo(mediaInfo);
      
      const video = mediaInfo.video_tracks[0];
      const audio = mediaInfo.audio_tracks[0];
      
      // Utiliser la fonction utilitaire pour déterminer la résolution
      const quality = getResolutionFromWidth(video?.width);
      
      setPresentationData({
        quality: quality === 'Unknown' ? '' : quality,
        format: mediaInfo.container || '',
        video_codec: video?.codec || '',
        audio_codec: audio?.codec || '',
        languages: mediaInfo.audio_tracks.map(a => a.language || 'Unknown').join(', '),
        subtitles: mediaInfo.subtitle_tracks.length > 0 
          ? mediaInfo.subtitle_tracks.map(s => s.language || 'Unknown').join(', ')
          : 'Aucun',
        size: formatSize(mediaInfo.file_size),
      });
    }
  }, [mediaInfo, setMediaInfo, setPresentationData]);

  const handleCopyRaw = () => {
    if (rawInfo) {
      copyRawInfo(rawInfo);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold">Informations MediaInfo</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowRaw(!showRaw)}
            className={`px-3 py-1.5 rounded text-sm ${
              showRaw ? 'bg-primary-500 text-gray-900' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            {showRaw ? 'Vue formatée' : 'Vue brute'}
          </button>
        </div>
      </div>

      {/* Info sur la source sélectionnée */}
      {isDirectory && (
        <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <FolderOpen className="w-5 h-5 text-blue-400" />
            <span className="font-medium text-blue-400">Dossier sélectionné</span>
          </div>
          <p className="text-sm text-gray-300 mb-1">{selectedItem?.name}</p>
          {firstVideoData && !firstVideoData.error ? (
            <p className="text-xs text-gray-400">
              MediaInfo basé sur : <span className="text-gray-300">{firstVideoData.name}</span>
            </p>
          ) : (
            <div className="flex items-center gap-1 text-yellow-500 text-xs">
              <AlertCircle className="w-3 h-3" />
              Aucun fichier vidéo trouvé dans ce dossier
            </div>
          )}
        </div>
      )}

      {/* Info série détectée */}
      {episodeInfo?.is_series && (
        <div className="bg-purple-900/30 border border-purple-700 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <span className="font-medium text-purple-400">Série TV détectée</span>
            <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-sm">
              {episodeInfo.is_complete_season 
                ? `Saison ${episodeInfo.season} complète`
                : `S${String(episodeInfo.season).padStart(2, '0')}E${String(episodeInfo.episode).padStart(2, '0')}`
              }
            </span>
          </div>
        </div>
      )}

      {isLoading || isLoadingFirstVideo ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : showRaw && rawInfo ? (
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">MediaInfo Raw Output</span>
            <button
              onClick={handleCopyRaw}
              className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded"
            >
              {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              {copied ? 'Copié!' : 'Copier'}
            </button>
          </div>
          <pre className="text-xs overflow-auto max-h-96 bg-gray-900 p-4 rounded">
            {rawInfo}
          </pre>
        </div>
      ) : mediaInfo ? (
        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="font-medium mb-3 text-primary-500">Général</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Fichier:</span>
                <p className="truncate">{mediaInfo.file_name}</p>
              </div>
              <div>
                <span className="text-gray-400">Taille:</span>
                <p>{formatSize(mediaInfo.file_size)}</p>
              </div>
              <div>
                <span className="text-gray-400">Conteneur:</span>
                <p>{mediaInfo.container || 'N/A'}</p>
              </div>
              <div>
                <span className="text-gray-400">Durée:</span>
                <p>{formatDuration(mediaInfo.duration)}</p>
              </div>
            </div>
          </div>

          {mediaInfo.video_tracks.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-3 text-blue-400">Vidéo</h3>
              {mediaInfo.video_tracks.map((track, i) => (
                <div key={i} className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Codec:</span>
                    <p>{track.codec || 'N/A'}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Résolution:</span>
                    <p>{track.width}x{track.height}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">FPS:</span>
                    <p>{track.framerate || 'N/A'}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {mediaInfo.audio_tracks.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-3 text-green-400">Audio</h3>
              <div className="space-y-3">
                {mediaInfo.audio_tracks.map((track, i) => (
                  <div key={i} className="grid grid-cols-4 gap-4 text-sm border-b border-gray-700 pb-2 last:border-0">
                    <div>
                      <span className="text-gray-400">Codec:</span>
                      <p>{track.codec || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Canaux:</span>
                      <p>{track.channels || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Langue:</span>
                      <p>{track.language || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Titre:</span>
                      <p className="truncate">{track.title || 'N/A'}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {mediaInfo.subtitle_tracks.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-3 text-yellow-400">Sous-titres</h3>
              <div className="space-y-2">
                {mediaInfo.subtitle_tracks.map((track, i) => (
                  <div key={i} className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Format:</span>
                      <p>{track.codec || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Langue:</span>
                      <p>{track.language || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Forcé:</span>
                      <p>{track.forced ? 'Oui' : 'Non'}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-400">
          Aucune information disponible
        </div>
      )}

      <div className="mt-6 flex items-center justify-between">
        <button
          onClick={() => setCurrentStep('tmdb')}
          className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentStep('rename')}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-gray-900 rounded-lg font-medium hover:bg-primary-400 transition-colors"
          >
            Continuer
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
