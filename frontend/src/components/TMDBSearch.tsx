import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Search, Film, Tv, Star, Loader2, X } from 'lucide-react';
import { tmdbApi, TMDBSearchResult, TMDBDetails } from '../services/api';

interface TMDBSearchProps {
  onSelect: (details: TMDBDetails) => void;
  onClose?: () => void;
  initialQuery?: string;
  autoSearch?: boolean;
}

export default function TMDBSearch({ onSelect, onClose, initialQuery, autoSearch }: TMDBSearchProps) {
  const [query, setQuery] = useState(initialQuery || '');
  const [searchType, setSearchType] = useState<'movie' | 'tv' | undefined>(undefined);
  const [results, setResults] = useState<TMDBSearchResult[]>([]);

  const searchMutation = useMutation({
    mutationFn: () => tmdbApi.search(query, searchType),
    onSuccess: (data: { results: TMDBSearchResult[] }) => {
      setResults(data.results);
    },
  });

  const detailsMutation = useMutation({
    mutationFn: async (item: TMDBSearchResult) => {
      if (item.type === 'movie') {
        return tmdbApi.getMovieDetails(item.id);
      } else {
        return tmdbApi.getTvDetails(item.id);
      }
    },
    onSuccess: (details: TMDBDetails) => {
      onSelect(details);
    },
  });

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      searchMutation.mutate();
    }
  };

  useEffect(() => {
    if (initialQuery && autoSearch) {
      setQuery(initialQuery);
      if (initialQuery.trim()) {
        searchMutation.mutate();
      }
    }
  }, [initialQuery, autoSearch]);

  const handleSelect = (item: TMDBSearchResult) => {
    detailsMutation.mutate(item);
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-primary-500">Recherche TMDB</h3>
        {onClose && (
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <form onSubmit={handleSearch} className="mb-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Rechercher un film ou une série..."
              className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-primary-500"
            />
          </div>
          <select
            value={searchType || ''}
            onChange={(e) => setSearchType(e.target.value as 'movie' | 'tv' | undefined || undefined)}
            className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Tous</option>
            <option value="movie">Films</option>
            <option value="tv">Séries</option>
          </select>
          <button
            type="submit"
            disabled={searchMutation.isPending || !query.trim()}
            className="px-4 py-2 bg-primary-500 text-gray-900 rounded-lg font-medium hover:bg-primary-400 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {searchMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              'Rechercher'
            )}
          </button>
        </div>
      </form>

      {results.length > 0 && (
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {results.map((item) => (
            <button
              key={`${item.type}-${item.id}`}
              onClick={() => handleSelect(item)}
              disabled={detailsMutation.isPending}
              className="w-full flex items-start gap-3 p-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-left transition-colors disabled:opacity-50"
            >
              {item.poster_path ? (
                <img
                  src={item.poster_path}
                  alt={item.title}
                  className="w-12 h-18 object-cover rounded"
                />
              ) : (
                <div className="w-12 h-18 bg-gray-600 rounded flex items-center justify-center">
                  {item.type === 'movie' ? (
                    <Film className="w-6 h-6 text-gray-400" />
                  ) : (
                    <Tv className="w-6 h-6 text-gray-400" />
                  )}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium truncate">{item.title}</span>
                  {item.year && (
                    <span className="text-sm text-gray-400">({item.year})</span>
                  )}
                </div>
                {item.original_title !== item.title && (
                  <p className="text-xs text-gray-500 truncate">{item.original_title}</p>
                )}
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-1.5 py-0.5 text-xs rounded ${
                    item.type === 'movie' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'
                  }`}>
                    {item.type === 'movie' ? 'Film' : 'Série'}
                  </span>
                  {item.vote_average > 0 && (
                    <span className="flex items-center gap-1 text-xs text-yellow-500">
                      <Star className="w-3 h-3 fill-current" />
                      {item.vote_average.toFixed(1)}
                    </span>
                  )}
                </div>
                {item.overview && (
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">{item.overview}</p>
                )}
              </div>
              {detailsMutation.isPending && detailsMutation.variables?.id === item.id && (
                <Loader2 className="w-4 h-4 animate-spin text-primary-500" />
              )}
            </button>
          ))}
        </div>
      )}

      {searchMutation.isSuccess && results.length === 0 && (
        <p className="text-center text-gray-500 py-4">Aucun résultat trouvé</p>
      )}
    </div>
  );
}
