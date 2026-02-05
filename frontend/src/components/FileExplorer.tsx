import { useState, useEffect, useMemo, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Folder, 
  File, 
  ChevronUp, 
  Home, 
  Check,
  Film,
  Music,
  Book,
  Archive,
  ArrowRight,
  Search,
  X
} from 'lucide-react';
import { filesApi } from '../services/api';
import { useAppStore } from '../stores/appStore';
import { formatSize } from '../utils/format';
import type { FileItem } from '../types';

const getFileIcon = (item: FileItem) => {
  if (item.is_dir) return <Folder className="w-5 h-5 text-primary-500" />;
  
  const ext = item.extension.toLowerCase();
  if (['.mkv', '.mp4', '.avi', '.mov', '.wmv'].includes(ext)) {
    return <Film className="w-5 h-5 text-blue-400" />;
  }
  if (['.mp3', '.flac', '.wav', '.aac', '.ogg'].includes(ext)) {
    return <Music className="w-5 h-5 text-green-400" />;
  }
  if (['.pdf', '.epub', '.mobi', '.cbr', '.cbz'].includes(ext)) {
    return <Book className="w-5 h-5 text-orange-400" />;
  }
  if (['.zip', '.rar', '.7z', '.tar', '.iso'].includes(ext)) {
    return <Archive className="w-5 h-5 text-purple-400" />;
  }
  return <File className="w-5 h-5 text-gray-400" />;
};

export default function FileExplorer() {
  const [currentPath, setCurrentPath] = useState<string>('');
  const [filterType, setFilterType] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<FileItem[] | null>(null);
  const { selectedFiles, addSelectedFile, removeSelectedFile, setCurrentStep } = useAppStore();

  const { data: root } = useQuery({
    queryKey: ['root'],
    queryFn: filesApi.getRoot,
  });

  const { data: directory, isLoading } = useQuery({
    queryKey: ['directory', currentPath, filterType],
    queryFn: () => filesApi.listDirectory(currentPath, filterType || undefined),
    enabled: currentPath !== '',
  });

  // Filtrage local réactif - filtre les items du dossier courant
  const filteredItems = useMemo(() => {
    if (searchResults) return searchResults;
    if (!searchQuery.trim()) return directory?.items || [];
    
    const query = searchQuery.toLowerCase();
    return (directory?.items || []).filter(item => 
      item.name.toLowerCase().includes(query)
    );
  }, [directory?.items, searchQuery, searchResults]);

  // Recherche globale (récursive) avec Enter
  const handleGlobalSearch = useCallback(async () => {
    if (!searchQuery.trim() || !currentPath) return;
    setIsSearching(true);
    try {
      const result = await filesApi.search(currentPath, searchQuery, filterType || undefined);
      setSearchResults(result.results);
    } finally {
      setIsSearching(false);
    }
  }, [searchQuery, currentPath, filterType]);

  useEffect(() => {
    if (root && currentPath === '') {
      setCurrentPath(root.path);
    }
  }, [root, currentPath]);

  const isSelected = (path: string) => selectedFiles.some(f => f.path === path);

  const handleItemClick = (item: FileItem) => {
    if (item.is_dir) {
      setCurrentPath(item.path);
    } else {
      if (isSelected(item.path)) {
        removeSelectedFile(item.path);
      } else {
        addSelectedFile(item);
      }
    }
  };

  const handleSelectFolder = () => {
    if (currentPath && directory) {
      const folderItem: FileItem = {
        path: currentPath,
        name: currentPath.split(/[/\\]/).pop() || currentPath,
        is_dir: true,
        size: 0,
        extension: ''
      };
      if (!isSelected(currentPath)) {
        addSelectedFile(folderItem);
      }
    }
  };

  const goToParent = () => {
    if (directory?.parent_path) {
      setCurrentPath(directory.parent_path);
    }
  };

  // Raccourci clavier: Backspace pour remonter au dossier parent
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Backspace ou Delete pour remonter
      if ((e.key === 'Backspace' || e.key === 'Delete') && directory?.parent_path) {
        // Éviter de capturer Backspace quand on est dans un input
        if (document.activeElement?.tagName !== 'INPUT') {
          e.preventDefault();
          goToParent();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [directory?.parent_path]);

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Explorateur de fichiers</h2>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                if (e.target.value === '') {
                  setSearchResults(null);
                }
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && searchQuery.trim() && currentPath) {
                  handleGlobalSearch();
                }
              }}
              placeholder="Rechercher..."
              className="bg-gray-700 border border-gray-600 rounded-lg pl-9 pr-8 py-1.5 text-sm w-48 focus:outline-none focus:border-primary-500"
            />
            {searchQuery && (
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSearchResults(null);
                }}
                className="absolute right-2 top-1/2 transform -translate-y-1/2"
              >
                <X className="w-4 h-4 text-gray-400 hover:text-white" />
              </button>
            )}
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-1.5 text-sm"
          >
            <option value="">Tous les fichiers</option>
            <option value="video">Vidéo uniquement</option>
          </select>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-4 bg-gray-800 rounded-lg p-2">
        {root && (
          <button
            onClick={() => setCurrentPath(root.path)}
            className={`flex items-center gap-1 px-3 py-1.5 rounded text-sm ${
              currentPath === root.path
                ? 'bg-primary-500/20 text-primary-500'
                : 'hover:bg-gray-700'
            }`}
          >
            <Home className="w-4 h-4" />
            {root.name}
          </button>
        )}
      </div>

      <div className="flex items-center gap-2 mb-4 bg-gray-800 rounded-lg p-2">
        <button
          onClick={goToParent}
          disabled={!directory?.parent_path}
          className="flex items-center gap-2 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-colors"
          title="Remonter au dossier parent (touche Backspace ou Delete)"
        >
          <ChevronUp className="w-4 h-4" />
          <span>Dossier parent</span>
        </button>
        <span className="text-sm text-gray-400 truncate flex-1">{currentPath}</span>
        <button
          onClick={handleSelectFolder}
          className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-sm"
        >
          Sélectionner ce dossier
        </button>
      </div>

      <div className="flex-1 bg-gray-800 rounded-lg overflow-hidden">
        <div className="h-full overflow-auto">
          {isLoading || isSearching ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-700 sticky top-0">
                <tr>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-400 w-8"></th>
                  <th className="text-left px-4 py-2 text-sm font-medium text-gray-400">
                    {(searchResults ? 'Résultats' : 'Éléments')} ({filteredItems.length})
                  </th>
                  <th className="text-right px-4 py-2 text-sm font-medium text-gray-400 w-24">Taille</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item: FileItem) => (
                  <tr
                    key={item.path}
                    onClick={() => handleItemClick(item)}
                    className={`cursor-pointer border-b border-gray-700 ${
                      isSelected(item.path)
                        ? 'bg-primary-500/20'
                        : 'hover:bg-gray-700'
                    }`}
                  >
                    <td className="px-4 py-2">
                      {!item.is_dir && (
                        <div className={`w-4 h-4 rounded border ${
                          isSelected(item.path)
                            ? 'bg-primary-500 border-primary-500'
                            : 'border-gray-500'
                        } flex items-center justify-center`}>
                          {isSelected(item.path) && <Check className="w-3 h-3 text-gray-900" />}
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-2">
                      <div className="flex items-center gap-2">
                        {getFileIcon(item)}
                        <span className="truncate">{item.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-2 text-right text-sm text-gray-400">
                      {!item.is_dir && formatSize(item.size)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {selectedFiles.length > 0 && (
        <div className="mt-4 p-4 bg-gray-800 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm text-gray-400">
                {selectedFiles.length} élément(s) sélectionné(s)
              </span>
              <div className="flex flex-wrap gap-2 mt-2">
                {selectedFiles.slice(0, 3).map(file => (
                  <span key={file.path} className="text-xs bg-gray-700 px-2 py-1 rounded">
                    {file.name}
                  </span>
                ))}
                {selectedFiles.length > 3 && (
                  <span className="text-xs text-gray-500">
                    +{selectedFiles.length - 3} autres
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={() => setCurrentStep('tmdb')}
              className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-gray-900 rounded-lg font-medium hover:bg-primary-400 transition-colors"
            >
              Continuer
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
