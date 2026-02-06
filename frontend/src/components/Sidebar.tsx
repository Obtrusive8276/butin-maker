import { 
  FolderOpen, 
  FileDown, 
  FileText, 
  CheckCircle,
  ChevronRight,
  PenLine,
  Search
} from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import type { Step } from '../types';

interface StepItem {
  id: Step;
  label: string;
  icon: React.ReactNode;
}

const steps: StepItem[] = [
  { id: 'files', label: 'Sélection fichiers', icon: <FolderOpen className="w-5 h-5" /> },
  { id: 'tmdb', label: 'Sélection TMDB', icon: <Search className="w-5 h-5" /> },
  { id: 'nfo', label: 'MediaInfo', icon: <FileText className="w-5 h-5" /> },
  { id: 'rename', label: 'Renommage', icon: <PenLine className="w-5 h-5" /> },
  { id: 'torrent', label: 'Création torrent', icon: <FileDown className="w-5 h-5" /> },
  { id: 'finalize', label: 'Finalisation', icon: <CheckCircle className="w-5 h-5" /> },
];

export default function Sidebar() {
  const { currentStep, setCurrentStep, selectedFiles, torrentResult, tmdbInfo, mediaInfo, releaseName } = useAppStore();

  const getStepStatus = (stepId: Step): 'completed' | 'current' | 'pending' => {
    if (stepId === currentStep) return 'current';
    switch (stepId) {
      case 'files':
        return selectedFiles.length > 0 ? 'completed' : 'pending';
      case 'tmdb':
        return tmdbInfo !== null ? 'completed' : 'pending';
      case 'nfo':
        return mediaInfo !== null ? 'completed' : 'pending';
      case 'rename':
        return releaseName !== '' ? 'completed' : 'pending';
      case 'torrent':
        return torrentResult?.success ? 'completed' : 'pending';
      case 'finalize':
        return 'pending';
      default:
        return 'pending';
    }
  };

  const canNavigateTo = (stepId: Step): boolean => {
    switch (stepId) {
      case 'files':
        return true;
      case 'tmdb':
        return selectedFiles.length > 0;
      case 'nfo':
        return selectedFiles.length > 0;
      case 'rename':
        return selectedFiles.length > 0;
      case 'torrent':
        return selectedFiles.length > 0;
      case 'finalize':
        return torrentResult?.success || false;
      default:
        return false;
    }
  };

  return (
    <aside className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div className="h-[57px] px-4 border-b border-gray-700 flex items-center">
        <div className="flex items-center gap-2">
          <img src="/logo.png" alt="Butin Maker" className="w-10 h-10 object-contain" />
          <span className="font-semibold">Butin Maker</span>
        </div>
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {steps.map((step) => {
            const status = getStepStatus(step.id);
            const canNavigate = canNavigateTo(step.id);

            return (
              <li key={step.id}>
                <button
                  onClick={() => canNavigate && setCurrentStep(step.id)}
                  disabled={!canNavigate}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    status === 'current'
                      ? 'bg-primary-500/20 text-primary-500'
                      : status === 'completed'
                      ? 'text-green-400 hover:bg-gray-700'
                      : canNavigate
                      ? 'text-gray-400 hover:bg-gray-700 hover:text-gray-200'
                      : 'text-gray-600 cursor-not-allowed'
                  }`}
                >
                  <span className={`flex-shrink-0 ${
                    status === 'completed' ? 'text-green-400' : ''
                  }`}>
                    {step.icon}
                  </span>
                  <span className="flex-1 text-left text-sm">{step.label}</span>
                  {status === 'current' && (
                    <ChevronRight className="w-4 h-4 text-primary-500" />
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-gray-700">
        <div className="text-xs text-gray-500">
          {selectedFiles.length > 0 && (
            <p>{selectedFiles.length} fichier(s) sélectionné(s)</p>
          )}
        </div>
      </div>
    </aside>
  );
}
