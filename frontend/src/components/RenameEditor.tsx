import { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { ArrowRight, ArrowLeft, Loader2, Copy, Check, RefreshCw, Link2 } from 'lucide-react';
import { tmdbApi, mediainfoApi } from '../services/api';
import { useAppStore } from '../stores/appStore';

export default function RenameEditor() {
  const { 
    selectedFiles, 
    mediaInfo, 
    setCurrentStep,
    releaseName,
    setReleaseName,
    tmdbInfo,
    seriesInfo,
    contentType,
    setNfoPath,
    mediaInfoFilePath,
    settings
  } = useAppStore();
  
  const [copied, setCopied] = useState(false);
  const [source, setSource] = useState('');
  const [edition, setEdition] = useState('');
  const [info, setInfo] = useState('');
  const [language, setLanguage] = useState('');
  const [hardlinkPath, setHardlinkPath] = useState('');
  const [nfoGenerated, setNfoGenerated] = useState(false);

  const selectedItem = selectedFiles[0];

  // Mutation pour générer le NFO avec le nom de release
  const generateNfoMutation = useMutation({
    mutationFn: () => mediainfoApi.generateNfo(mediaInfoFilePath || '', releaseName || undefined),
    onSuccess: (data) => {
      if (data.success) {
        setNfoPath(data.file_path);
        setNfoGenerated(true);
      }
    },
  });

  const generateNameMutation = useMutation({
    mutationFn: () => tmdbApi.generateReleaseName(
      tmdbInfo?.title || selectedItem?.name || '',
      tmdbInfo?.year || null,
      mediaInfo || {},
      {
        source: source || undefined,
        contentType: contentType,
        season: seriesInfo.season || undefined,
        episode: seriesInfo.episode || undefined,
        isCompleteSeason: seriesInfo.isCompleteSeason,
        edition: edition || undefined,
        info: info || undefined,
        language: language || undefined,
      }
    ),
    onSuccess: (data) => {
      setReleaseName(data.release_name);
      if (selectedItem) {
        const ext = selectedItem.name.includes('.') 
          ? '.' + selectedItem.name.split('.').pop() 
          : '';
        const basePath = settings?.paths?.hardlink_path || '/data';
        const separator = basePath.endsWith('/') ? '' : '/';
        setHardlinkPath(`${basePath}${separator}${data.release_name}${selectedItem.is_dir ? '' : ext}`);
      }
    },
  });

  useEffect(() => {
    if (selectedItem && (tmdbInfo || mediaInfo)) {
      generateNameMutation.mutate();
    }
  }, [tmdbInfo, mediaInfo, source, edition, info, language]);

  const handleCopy = () => {
    navigator.clipboard.writeText(releaseName);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReleaseNameChange = (newName: string) => {
    setReleaseName(newName);
    // Mettre à jour le hardlink avec le nouveau nom
    if (selectedItem) {
      const ext = selectedItem.name.includes('.') 
        ? '.' + selectedItem.name.split('.').pop() 
        : '';
      setHardlinkPath(`/data/${newName}${selectedItem.is_dir ? '' : ext}`);
    }
  };

  const sourceOptions = [
    '', 'BluRay', 'WEB', 'WEB-DL', 'WEBRip', 'DVDRip', 'HDTV', 'REMUX', 'HDLight'
  ];

  const editionOptions = [
    '', 'DC', 'EXTENDED', 'REMASTERED', 'UNRATED', 'FiNAL.CUT', 'THEATRiCAL'
  ];

  const infoOptions = [
    '', 'REPACK', 'PROPER', 'CUSTOM', 'RERip'
  ];

  const languageOptions = [
    { value: '', label: 'Auto-détection' },
    { value: 'MULTi.TrueFrench', label: 'MULTi.TrueFrench (FR France + EN)' },
    { value: 'MULTi.VFQ', label: 'MULTi.VFQ (FR Québec + EN)' },
    { value: 'MULTi.VFi', label: 'MULTi.VFi (FR International + EN)' },
    { value: 'MULTi', label: 'MULTi (plusieurs langues)' },
    { value: 'TrueFrench', label: 'TrueFrench (FR France seul)' },
    { value: 'VFQ', label: 'VFQ (FR Québec seul)' },
    { value: 'FRENCH', label: 'FRENCH' },
    { value: 'VOSTFR', label: 'VOSTFR' },
    { value: 'ENGLISH', label: 'ENGLISH' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Renommage</h2>
      </div>

      {/* Fichier source */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-3">Fichier source</h3>
        <div className="text-gray-300 font-mono text-sm break-all">
          {selectedItem?.path || 'Aucun fichier sélectionné'}
        </div>
      </div>

      {/* Options de renommage */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Options de renommage</h3>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Langue</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
            >
              {languageOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Source</label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
            >
              {sourceOptions.map(opt => (
                <option key={opt} value={opt}>{opt || 'Auto-détection'}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Édition</label>
            <select
              value={edition}
              onChange={(e) => setEdition(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
            >
              {editionOptions.map(opt => (
                <option key={opt} value={opt}>{opt || 'Aucune'}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Info</label>
            <select
              value={info}
              onChange={(e) => setInfo(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
            >
              {infoOptions.map(opt => (
                <option key={opt} value={opt}>{opt || 'Aucune'}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={() => generateNameMutation.mutate()}
          disabled={generateNameMutation.isPending}
          className="mt-4 flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          {generateNameMutation.isPending ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          Régénérer le nom
        </button>
      </div>

      {/* Nom de release généré */}
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold">Nom de release</h3>
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm"
          >
            {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
            {copied ? 'Copié!' : 'Copier'}
          </button>
        </div>
        
        {generateNameMutation.isPending ? (
          <div className="flex items-center gap-2 text-gray-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            Génération en cours...
          </div>
        ) : (
          <input
            type="text"
            value={releaseName}
            onChange={(e) => handleReleaseNameChange(e.target.value)}
            className="w-full bg-gray-900 rounded-lg p-4 font-mono text-primary-400 text-lg break-all border border-gray-700 focus:border-primary-500 focus:outline-none"
            placeholder="Nom de release..."
          />
        )}
        <p className="text-xs text-gray-500 mt-2">
          Vous pouvez modifier ce nom manuellement. Il sera utilisé pour le fichier renommé.
        </p>
      </div>

      {/* Hardlink */}
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Link2 className="w-5 h-5 text-primary-500" />
          <h3 className="text-lg font-semibold">Hardlink</h3>
        </div>
        
        <p className="text-gray-400 text-sm mb-3">
          Un hardlink sera créé pour renommer le fichier sans dupliquer l'espace disque.
        </p>

        <div className="space-y-2">
          <div>
            <span className="text-sm text-gray-500">Source:</span>
            <div className="text-gray-300 font-mono text-sm">{selectedItem?.path}</div>
          </div>
          <div>
            <span className="text-sm text-gray-500">Destination:</span>
            <div className="text-primary-400 font-mono text-sm">{hardlinkPath || 'Non défini'}</div>
          </div>
        </div>

        <div className="mt-4 p-3 bg-yellow-900/30 border border-yellow-700 rounded-lg">
          <p className="text-yellow-400 text-sm">
            ⚠️ Le hardlink sera créé lors de la création du torrent à l'étape suivante.
          </p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentStep('nfo')}
          className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          MediaInfo
        </button>
        <div className="flex items-center gap-4">
          {generateNfoMutation.isPending && (
            <div className="flex items-center gap-2 text-gray-400 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" />
              Génération NFO...
            </div>
          )}
          {nfoGenerated && (
            <div className="flex items-center gap-2 text-green-400 text-sm">
              <Check className="w-4 h-4" />
              NFO généré
            </div>
          )}
          <button
            onClick={() => {
              // Générer le NFO avec le nom de release actuel, puis passer à l'étape suivante
              if (mediaInfoFilePath && releaseName) {
                generateNfoMutation.mutate(undefined, {
                  onSuccess: () => setCurrentStep('torrent')
                });
              } else {
                setCurrentStep('torrent');
              }
            }}
            disabled={generateNfoMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-gray-900 rounded-lg transition-colors disabled:opacity-50"
          >
            Création torrent
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
