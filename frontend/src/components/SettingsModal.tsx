import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Save, TestTube, Loader2, Check, AlertCircle } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { settingsApi, torrentApi } from '../services/api';
import type { Settings } from '../types';

export default function SettingsModal() {
  const { settings, setSettings, setIsSettingsOpen } = useAppStore();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState<Settings>({
    qbittorrent: {
      host: 'http://localhost',
      port: 8080,
      username: 'admin',
      password: ''
    },
    tracker: {
      announce_url: '',
      upload_url: ''
    },
    paths: {
      default_browse_path: '',
      hardlink_path: '',
      qbittorrent_download_path: '',
      output_path: ''
    },
    tmdb: {
      api_key: ''
    }
  });

  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [isTesting, setIsTesting] = useState(false);

  useEffect(() => {
    if (settings) {
      setFormData(settings);
    }
  }, [settings]);

  const saveMutation = useMutation({
    mutationFn: settingsApi.save,
    onSuccess: () => {
      setSettings(formData);
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      setIsSettingsOpen(false);
    },
  });

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const result = await torrentApi.testConnection(
        formData.qbittorrent.host,
        formData.qbittorrent.port,
        formData.qbittorrent.username,
        formData.qbittorrent.password
      );
      setTestResult(result);
    } catch (error) {
      setTestResult({ success: false, message: 'Erreur de connexion' });
    }
    setIsTesting(false);
  };

  const handleSave = () => {
    saveMutation.mutate(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold">Paramètres</h2>
          <button
            onClick={() => setIsSettingsOpen(false)}
            className="p-1 hover:bg-gray-700 rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <section>
            <h3 className="font-medium mb-4 text-primary-500">qBittorrent</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Hôte</label>
                <input
                  type="text"
                  value={formData.qbittorrent.host}
                  onChange={(e) => setFormData({
                    ...formData,
                    qbittorrent: { ...formData.qbittorrent, host: e.target.value }
                  })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
                  placeholder="http://localhost"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Port</label>
                <input
                  type="number"
                  value={formData.qbittorrent.port}
                  onChange={(e) => setFormData({
                    ...formData,
                    qbittorrent: { ...formData.qbittorrent, port: parseInt(e.target.value) || 8080 }
                  })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
                  placeholder="8080"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Nom d'utilisateur</label>
                <input
                  type="text"
                  value={formData.qbittorrent.username}
                  onChange={(e) => setFormData({
                    ...formData,
                    qbittorrent: { ...formData.qbittorrent, username: e.target.value }
                  })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
                  placeholder="admin"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Mot de passe</label>
                <input
                  type="password"
                  value={formData.qbittorrent.password}
                  onChange={(e) => setFormData({
                    ...formData,
                    qbittorrent: { ...formData.qbittorrent, password: e.target.value }
                  })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              onClick={handleTestConnection}
              disabled={isTesting}
              className="mt-4 flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
            >
              {isTesting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <TestTube className="w-4 h-4" />
              )}
              Tester la connexion
            </button>

            {testResult && (
              <div className={`mt-3 flex items-center gap-2 text-sm ${
                testResult.success ? 'text-green-400' : 'text-red-400'
              }`}>
                {testResult.success ? (
                  <Check className="w-4 h-4" />
                ) : (
                  <AlertCircle className="w-4 h-4" />
                )}
                {testResult.message}
              </div>
            )}
          </section>

          <section>
            <h3 className="font-medium mb-4 text-primary-500">Tracker La Cale</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">URL d'annonce (avec passkey)</label>
                <input
                  type="text"
                  value={formData.tracker.announce_url}
                  onChange={(e) => setFormData({
                    ...formData,
                    tracker: { ...formData.tracker, announce_url: e.target.value }
                  })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
                  placeholder="https://la-cale.example/announce?passkey=XXXXX"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Cette URL sera intégrée dans le fichier .torrent
                </p>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">URL d'upload</label>
                <input
                  type="text"
                  value={formData.tracker.upload_url}
                  onChange={(e) => setFormData({
                    ...formData,
                    tracker: { ...formData.tracker, upload_url: e.target.value }
                  })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
                  placeholder="https://la-cale.example/upload"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Page d'upload sur laquelle vous serez redirigé à la fin
                </p>
              </div>
            </div>
          </section>

          <section>
            <h3 className="font-medium mb-4 text-primary-500">Chemins</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Chemin de navigation par défaut</label>
                <input
                  type="text"
                  value={formData.paths.default_browse_path}
                  onChange={(e) => setFormData({
                    ...formData,
                    paths: { ...formData.paths, default_browse_path: e.target.value }
                  })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
                  placeholder="/data"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Dossier ouvert par défaut dans l'explorateur de fichiers
                </p>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Dossier de destination des hardlinks</label>
                <input
                  type="text"
                  value={formData.paths.hardlink_path}
                  onChange={(e) => setFormData({
                    ...formData,
                    paths: { ...formData.paths, hardlink_path: e.target.value }
                  })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
                  placeholder="/data/uploads"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Dossier où seront créés les hardlinks avec le nom de release
                </p>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Dossier de téléchargement qBittorrent</label>
                <input
                  type="text"
                  value={formData.paths.qbittorrent_download_path}
                  onChange={(e) => setFormData({
                    ...formData,
                    paths: { ...formData.paths, qbittorrent_download_path: e.target.value }
                  })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
                  placeholder="/data/uploads"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Dossier utilisé par qBittorrent pour le seeding (save_path)
                </p>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Dossier de sortie</label>
                <input
                  type="text"
                  value={formData.paths.output_path}
                  onChange={(e) => setFormData({
                    ...formData,
                    paths: { ...formData.paths, output_path: e.target.value }
                  })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
                  placeholder="/data/uploads"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Dossier où seront stockés les fichiers générés (torrents, NFO)
                </p>
              </div>
            </div>
          </section>

          <section>
            <h3 className="font-medium mb-4 text-primary-500">TMDB</h3>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Clé API</label>
              <input
                type="password"
                value={formData.tmdb.api_key}
                onChange={(e) => setFormData({
                  ...formData,
                  tmdb: { ...formData.tmdb, api_key: e.target.value }
                })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
                placeholder="Clé TMDB"
              />
              <p className="text-xs text-gray-500 mt-1">
                Utilisée si la variable d&apos;environnement TMDB_API_KEY n&apos;est pas définie.
              </p>
            </div>
          </section>
        </div>

        <div className="flex items-center justify-end gap-3 p-4 border-t border-gray-700">
          <button
            onClick={() => setIsSettingsOpen(false)}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
          >
            Annuler
          </button>
          <button
            onClick={handleSave}
            disabled={saveMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-gray-900 rounded font-medium hover:bg-primary-400 transition-colors disabled:opacity-50"
          >
            {saveMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            Sauvegarder
          </button>
        </div>
      </div>
    </div>
  );
}
