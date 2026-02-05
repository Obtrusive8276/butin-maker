import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Loader2, AlertTriangle, Settings } from 'lucide-react';
import { tmdbApi, TMDBDetails } from '../services/api';
import { useAppStore } from '../stores/appStore';
import TMDBSearch from './TMDBSearch';

export default function TMDBSelect() {
  const { selectedFiles, setCurrentStep, setTmdbInfo, setContentType, setIsSettingsOpen } = useAppStore();
  const selectedItem = selectedFiles[0];

  const { data: tmdbStatus, isLoading: isLoadingStatus } = useQuery({
    queryKey: ['tmdb-status'],
    queryFn: () => tmdbApi.getStatus(),
  });

  const { data: extractedTitle, isLoading } = useQuery({
    queryKey: ['extract-title', selectedItem?.name],
    queryFn: () => (selectedItem ? tmdbApi.extractTitle(selectedItem.name) : null),
    enabled: !!selectedItem && tmdbStatus?.configured,
  });

  const handleSelect = (details: TMDBDetails) => {
    setTmdbInfo({
      id: details.id,
      title: details.title,
      original_title: details.original_title,
      year: details.year,
      poster_path: details.poster_path,
      overview: details.overview,
      vote_average: details.vote_average,
      genres: details.genres,
      type: details.type,
    });
    setContentType(details.type);
    setCurrentStep('nfo');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Sélection TMDB</h2>
        <button
          onClick={() => setCurrentStep('files')}
          className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Fichiers
        </button>
      </div>

      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2">Fichier sélectionné</h3>
        <div className="text-gray-300 font-mono text-sm break-all">
          {selectedItem?.path || 'Aucun fichier sélectionné'}
        </div>
      </div>

      {isLoadingStatus ? (
        <div className="flex items-center gap-2 text-gray-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          Vérification de la configuration TMDB...
        </div>
      ) : !tmdbStatus?.configured ? (
        <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <AlertTriangle className="w-6 h-6 text-yellow-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-yellow-500 mb-2">
                Clé API TMDB non configurée
              </h3>
              <p className="text-gray-300 mb-4">
                Pour rechercher des films et séries sur TMDB, vous devez configurer une clé API.
                Vous pouvez obtenir une clé gratuite sur{' '}
                <a
                  href="https://www.themoviedb.org/settings/api"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-400 hover:underline"
                >
                  themoviedb.org
                </a>
              </p>
              <button
                onClick={() => setIsSettingsOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-gray-900 rounded-lg font-medium hover:bg-primary-400 transition-colors"
              >
                <Settings className="w-4 h-4" />
                Ouvrir les paramètres
              </button>
            </div>
          </div>
        </div>
      ) : isLoading ? (
        <div className="flex items-center gap-2 text-gray-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          Extraction du titre...
        </div>
      ) : (
        <TMDBSearch
          initialQuery={extractedTitle?.extracted_title || ''}
          autoSearch
          onSelect={handleSelect}
        />
      )}
    </div>
  );
}
