import { create } from 'zustand';
import type { Step, FileItem, Settings, TorrentResponse, MediaInfo, PresentationData } from '../types';

interface TMDBInfo {
  id: number;
  title: string;
  original_title: string;
  year: string | null;
  poster_path: string | null;
  overview: string;
  vote_average: number;
  genres: string;
  type: 'movie' | 'tv';
}

interface SeriesInfo {
  season: number | null;
  episode: number | null;
  isCompleteSeason: boolean;
}

interface AppState {
  currentStep: Step;
  setCurrentStep: (step: Step) => void;

  selectedFiles: FileItem[];
  setSelectedFiles: (files: FileItem[]) => void;
  addSelectedFile: (file: FileItem) => void;
  removeSelectedFile: (path: string) => void;
  clearSelectedFiles: () => void;

  settings: Settings | null;
  setSettings: (settings: Settings) => void;

  torrentResult: TorrentResponse | null;
  setTorrentResult: (result: TorrentResponse | null) => void;

  mediaInfo: MediaInfo | null;
  setMediaInfo: (info: MediaInfo | null) => void;

  nfoPath: string | null;
  setNfoPath: (path: string | null) => void;

  presentationData: PresentationData;
  setPresentationData: (data: Partial<PresentationData>) => void;
  resetPresentationData: () => void;

  generatedBBCode: string;
  setGeneratedBBCode: (bbcode: string) => void;

  selectedTags: string[];
  setSelectedTags: (tags: string[]) => void;
  toggleTag: (tag: string) => void;

  isSettingsOpen: boolean;
  setIsSettingsOpen: (open: boolean) => void;

  tmdbInfo: TMDBInfo | null;
  setTmdbInfo: (info: TMDBInfo | null) => void;

  releaseName: string;
  setReleaseName: (name: string) => void;

  seriesInfo: SeriesInfo;
  setSeriesInfo: (info: Partial<SeriesInfo>) => void;
  resetSeriesInfo: () => void;

  contentType: 'movie' | 'tv';
  setContentType: (type: 'movie' | 'tv') => void;

  mediaInfoFilePath: string | null;
  setMediaInfoFilePath: (path: string | null) => void;
}

const defaultPresentationData: PresentationData = {
  poster_url: '',
  title: '',
  rating: '',
  genre: '',
  synopsis: '',
  quality: '',
  format: '',
  video_codec: '',
  audio_codec: '',
  languages: '',
  subtitles: '',
  size: '',
};

export const useAppStore = create<AppState>((set) => ({
  currentStep: 'files',
  setCurrentStep: (step) => set({ currentStep: step }),

  selectedFiles: [],
  setSelectedFiles: (files) => set({ selectedFiles: files }),
  addSelectedFile: (file) => set((state) => ({
    selectedFiles: state.selectedFiles.some(f => f.path === file.path)
      ? state.selectedFiles
      : [...state.selectedFiles, file]
  })),
  removeSelectedFile: (path) => set((state) => ({
    selectedFiles: state.selectedFiles.filter(f => f.path !== path)
  })),
  clearSelectedFiles: () => set({ selectedFiles: [] }),

  settings: null,
  setSettings: (settings) => set({ settings }),

  torrentResult: null,
  setTorrentResult: (result) => set({ torrentResult: result }),

  mediaInfo: null,
  setMediaInfo: (info) => set({ mediaInfo: info }),

  nfoPath: null,
  setNfoPath: (path) => set({ nfoPath: path }),

  presentationData: defaultPresentationData,
  setPresentationData: (data) => set((state) => ({
    presentationData: { ...state.presentationData, ...data }
  })),
  resetPresentationData: () => set({ presentationData: defaultPresentationData }),

  generatedBBCode: '',
  setGeneratedBBCode: (bbcode) => set({ generatedBBCode: bbcode }),

  selectedTags: [],
  setSelectedTags: (tags) => set({ selectedTags: tags }),
  toggleTag: (tag) => set((state) => ({
    selectedTags: state.selectedTags.includes(tag)
      ? state.selectedTags.filter(t => t !== tag)
      : [...state.selectedTags, tag]
  })),

  isSettingsOpen: false,
  setIsSettingsOpen: (open) => set({ isSettingsOpen: open }),

  tmdbInfo: null,
  setTmdbInfo: (info) => set({ tmdbInfo: info }),

  releaseName: '',
  setReleaseName: (name) => set({ releaseName: name }),

  seriesInfo: { season: null, episode: null, isCompleteSeason: false },
  setSeriesInfo: (info) => set((state) => ({
    seriesInfo: { ...state.seriesInfo, ...info }
  })),
  resetSeriesInfo: () => set({ seriesInfo: { season: null, episode: null, isCompleteSeason: false } }),

  contentType: 'movie',
  setContentType: (type) => set({ contentType: type }),

  mediaInfoFilePath: null,
  setMediaInfoFilePath: (path) => set({ mediaInfoFilePath: path }),
}));
