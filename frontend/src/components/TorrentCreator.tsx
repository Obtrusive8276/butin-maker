import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { FileDown, Check, AlertCircle, ArrowRight, ArrowLeft, Loader2 } from 'lucide-react';
import { torrentApi } from '../services/api';
import { useAppStore } from '../stores/appStore';

export default function TorrentCreator() {
  const { selectedFiles, settings, torrentResult, setTorrentResult, setCurrentStep, releaseName } = useAppStore();
  const [torrentName, setTorrentName] = useState('');
  const [pieceSize, setPieceSize] = useState<number | undefined>(undefined);
  const [trackerUrl, setTrackerUrl] = useState(settings?.tracker.announce_url || '');

  const createMutation = useMutation({
    mutationFn: torrentApi.createTorrent,
    onSuccess: (data) => {
      setTorrentResult(data);
    },
  });

  const sourcePath = selectedFiles.length > 0 ? selectedFiles[0].path : '';
  const defaultName = releaseName || (selectedFiles.length > 0 ? selectedFiles[0].name : '');

  const handleCreateTorrent = () => {
    if (!sourcePath) return;

    createMutation.mutate({
      source_path: sourcePath,
      name: torrentName || defaultName || undefined,
      piece_size: pieceSize,
      private: true,
      tracker_url: trackerUrl || undefined,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Création du Torrent</h2>
      </div>

      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-3">Source</h3>
        <div className="bg-gray-700 rounded p-3 text-sm">
          <p className="text-gray-400">Chemin:</p>
          <p className="truncate">{sourcePath}</p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Options du Torrent</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Nom du torrent (optionnel)
            </label>
            <input
              type="text"
              value={torrentName}
              onChange={(e) => setTorrentName(e.target.value)}
              placeholder={defaultName}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Taille des pièces
            </label>
            <select
              value={pieceSize || ''}
              onChange={(e) => setPieceSize(e.target.value ? parseInt(e.target.value) : undefined)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
            >
              <option value="">Automatique</option>
              <option value="16384">16 KB</option>
              <option value="32768">32 KB</option>
              <option value="65536">64 KB</option>
              <option value="131072">128 KB</option>
              <option value="262144">256 KB</option>
              <option value="524288">512 KB</option>
              <option value="1048576">1 MB</option>
              <option value="2097152">2 MB</option>
              <option value="4194304">4 MB</option>
              <option value="8388608">8 MB</option>
              <option value="16777216">16 MB</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              URL du tracker (announce)
            </label>
            <input
              type="text"
              value={trackerUrl}
              onChange={(e) => setTrackerUrl(e.target.value)}
              placeholder="https://tracker.example.com/announce?passkey=xxx"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
            />
            {!trackerUrl && (
              <p className="text-xs text-yellow-500 mt-1">Aucun tracker - le torrent sera créé sans tracker</p>
            )}
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Check className="w-4 h-4 text-green-400" />
            <span>Torrent privé activé</span>
          </div>
        </div>
      </div>

      {torrentResult && (
        <div className={`rounded-lg p-6 mb-6 ${
          torrentResult.success ? 'bg-green-900/30 border border-green-700' : 'bg-red-900/30 border border-red-700'
        }`}>
          {torrentResult.success ? (
            <>
              <div className="flex items-center gap-2 mb-4">
                <Check className="w-5 h-5 text-green-400" />
                <span className="font-medium text-green-400">Torrent créé avec succès!</span>
              </div>
              <div className="text-sm space-y-1 text-gray-300">
                <p><span className="text-gray-400">Nom:</span> {torrentResult.torrent_name}</p>
                <p><span className="text-gray-400">Hash:</span> {torrentResult.info_hash}</p>
                <p><span className="text-gray-400">Pièces:</span> {torrentResult.piece_count}</p>
              </div>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <span className="text-red-400">{torrentResult.error}</span>
            </div>
          )}
        </div>
      )}

      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentStep('rename')}
          className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={handleCreateTorrent}
            disabled={!sourcePath || createMutation.isPending}
            className="flex items-center gap-2 px-6 py-2 bg-primary-500 text-gray-900 rounded-lg font-medium hover:bg-primary-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Création...
              </>
            ) : (
              <>
                <FileDown className="w-4 h-4" />
                Créer le torrent
              </>
            )}
          </button>

          {torrentResult?.success && (
            <button
              onClick={() => setCurrentStep('finalize')}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg font-medium transition-colors"
            >
              Continuer
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
