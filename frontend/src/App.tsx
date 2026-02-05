import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Settings } from 'lucide-react';
import { useAppStore } from './stores/appStore';
import { settingsApi } from './services/api';
import Sidebar from './components/Sidebar';
import FileExplorer from './components/FileExplorer';
import TMDBSelect from './components/TMDBSelect';
import TorrentCreator from './components/TorrentCreator';
import MediaInfoViewer from './components/MediaInfoViewer';
import RenameEditor from './components/RenameEditor';
import Finalize from './components/Finalize';
import SettingsModal from './components/SettingsModal';

const pirateTitles: Record<string, string> = {
  files: '🗺️ Repérage du butin',
  tmdb: '🔭 Identification du trésor',
  nfo: '📜 Inventaire de la cargaison',
  rename: '🏴‍☠️ Marquage du butin',
  torrent: '⚓ Préparation de l\'expédition',
  finalize: '💰 À l\'abordage !',
};

function App() {
  const { currentStep, isSettingsOpen, setIsSettingsOpen, setSettings } = useAppStore();

  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsApi.get,
  });

  useEffect(() => {
    if (settings) {
      setSettings(settings);
    }
  }, [settings, setSettings]);

  const renderStep = () => {
    switch (currentStep) {
      case 'files':
        return <FileExplorer />;
      case 'tmdb':
        return <TMDBSelect />;
      case 'nfo':
        return <MediaInfoViewer />;
      case 'rename':
        return <RenameEditor />;
      case 'torrent':
        return <TorrentCreator />;
      case 'finalize':
        return <Finalize />;
      default:
        return <FileExplorer />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-[57px] bg-gray-800 border-b border-gray-700 px-6 flex items-center justify-between">
          <h1 className="text-lg font-bold text-primary-500">
            {pirateTitles[currentStep] || 'Butin Maker'}
          </h1>
          <button
            onClick={() => setIsSettingsOpen(true)}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            title="Paramètres"
          >
            <Settings className="w-5 h-5" />
          </button>
        </header>

        <main className="flex-1 overflow-auto p-6">
          {renderStep()}
        </main>
      </div>

      {isSettingsOpen && <SettingsModal />}
    </div>
  );
}

export default App;
