import axios from 'axios';
import type { 
  DirectoryListing, 
  Settings, 
  TorrentCreateRequest, 
  TorrentResponse,
  MediaInfo,
  PresentationData,
  LaCaleUploadRequest,
  LaCaleUploadResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const filesApi = {
  getRoot: async () => {
    const response = await api.get<{ path: string; name: string; is_dir: boolean }>('/files/root');
    return response.data;
  },

  listDirectory: async (path: string, filterType?: string): Promise<DirectoryListing> => {
    const params = new URLSearchParams({ path });
    if (filterType) params.append('filter_type', filterType);
    const response = await api.get<DirectoryListing>(`/files/list?${params}`);
    return response.data;
  },

  getFileInfo: async (path: string) => {
    const response = await api.get(`/files/info?path=${encodeURIComponent(path)}`);
    return response.data;
  },

  getDirectorySize: async (path: string) => {
    const response = await api.get(`/files/directory-size?path=${encodeURIComponent(path)}`);
    return response.data;
  },

  getFirstVideo: async (path: string) => {
    const response = await api.get(`/files/first-video?path=${encodeURIComponent(path)}`);
    return response.data;
  },

  getVideoCount: async (path: string) => {
    const response = await api.get(`/files/video-count?path=${encodeURIComponent(path)}`);
    return response.data;
  },

  search: async (path: string, query: string, filterType?: string) => {
    const params = new URLSearchParams({ path, query });
    if (filterType) params.append('filter_type', filterType);
    const response = await api.get(`/files/search?${params}`);
    return response.data;
  },

  createHardlink: async (sourcePath: string, destinationPath: string) => {
    const response = await api.post('/files/create-hardlink', {
      source_path: sourcePath,
      destination_path: destinationPath
    });
    return response.data;
  },
};

export const torrentApi = {
  testConnection: async (host: string, port: number, username: string, password: string) => {
    const response = await api.post<{ success: boolean; message: string }>('/torrent/test-connection', {
      host,
      port,
      username,
      password,
    });
    return response.data;
  },

  createTorrent: async (data: TorrentCreateRequest): Promise<TorrentResponse> => {
    const response = await api.post<TorrentResponse>('/torrent/create', data);
    return response.data;
  },

  downloadTorrent: (filename: string) => {
    return `${API_BASE}/torrent/download/${encodeURIComponent(filename)}`;
  },

  addForSeeding: async (torrentPath: string, contentPath: string) => {
    const response = await api.post('/torrent/add-for-seeding', {
      torrent_path: torrentPath,
      content_path: contentPath,
    });
    return response.data;
  },
};

export const mediainfoApi = {
  analyze: async (path: string): Promise<MediaInfo> => {
    const response = await api.get<MediaInfo>(`/mediainfo/analyze?path=${encodeURIComponent(path)}`);
    return response.data;
  },

  getRaw: async (path: string): Promise<string> => {
    const response = await api.get(`/mediainfo/raw?path=${encodeURIComponent(path)}`);
    return response.data;
  },

  generateNfo: async (path: string, releaseName?: string) => {
    let url = `/mediainfo/generate-nfo?path=${encodeURIComponent(path)}`;
    if (releaseName) {
      url += `&release_name=${encodeURIComponent(releaseName)}`;
    }
    const response = await api.post(url);
    return response.data;
  },

  downloadNfo: (filename: string) => {
    return `${API_BASE}/mediainfo/download-nfo/${encodeURIComponent(filename)}`;
  },
};

export const presentationApi = {
  generate: async (data: PresentationData): Promise<{ bbcode: string }> => {
    const response = await api.post<{ bbcode: string }>('/presentation/generate', data);
    return response.data;
  },

  getTemplate: async (): Promise<{ template: string }> => {
    const response = await api.get<{ template: string }>('/presentation/template');
    return response.data;
  },

  saveTemplate: async (template: string) => {
    const response = await api.post('/presentation/template', { template });
    return response.data;
  },
};

export const settingsApi = {
  get: async (): Promise<Settings> => {
    const response = await api.get<Settings>('/settings/');
    return response.data;
  },

  save: async (settings: Settings) => {
    const response = await api.post('/settings/', settings);
    return response.data;
  },

  updateQBittorrent: async (data: Settings['qbittorrent']) => {
    const response = await api.patch('/settings/qbittorrent', data);
    return response.data;
  },

  updateTracker: async (data: Settings['tracker']) => {
    const response = await api.patch('/settings/tracker', data);
    return response.data;
  },
};

export interface TMDBSearchResult {
  id: number;
  title: string;
  original_title: string;
  year: string | null;
  poster_path: string | null;
  overview: string;
  vote_average: number;
  type: 'movie' | 'tv';
}

export interface TMDBDetails extends TMDBSearchResult {
  release_date: string;
  backdrop_path: string | null;
  genres: string;
  runtime?: number;
  tagline?: string;
  imdb_id?: string;
  number_of_seasons?: number;
  number_of_episodes?: number;
  status?: string;
}

export interface TMDBStatus {
  configured: boolean;
  message: string;
}

export const tmdbApi = {
  getStatus: async (): Promise<TMDBStatus> => {
    const response = await api.get('/tmdb/status');
    return response.data;
  },

  search: async (query: string, type?: 'movie' | 'tv'): Promise<{ results: TMDBSearchResult[] }> => {
    const params = new URLSearchParams({ query });
    if (type) params.append('type', type);
    const response = await api.get(`/tmdb/search?${params}`);
    return response.data;
  },

  getMovieDetails: async (movieId: number): Promise<TMDBDetails> => {
    const response = await api.get(`/tmdb/movie/${movieId}`);
    return response.data;
  },

  getTvDetails: async (tvId: number): Promise<TMDBDetails> => {
    const response = await api.get(`/tmdb/tv/${tvId}`);
    return response.data;
  },

  generateReleaseName: async (
    title: string,
    year: string | null,
    mediaInfo: object,
    options?: {
      source?: string;
      group?: string;
      contentType?: 'movie' | 'tv';
      season?: number;
      episode?: number;
      isCompleteSeason?: boolean;
      isCompleteSeries?: boolean;
      isFinalEpisode?: boolean;
      episodeOnly?: boolean;
      edition?: string;
      info?: string;
      language?: string;
    }
  ): Promise<{ release_name: string }> => {
    const params = new URLSearchParams({ title });
    if (year) params.append('year', year);
    if (options?.source) params.append('source', options.source);
    if (options?.group) params.append('group', options.group);
    if (options?.contentType) params.append('content_type', options.contentType);
    if (options?.season !== undefined) params.append('season', options.season.toString());
    if (options?.episode !== undefined) params.append('episode', options.episode.toString());
    if (options?.isCompleteSeason) params.append('is_complete_season', 'true');
    if (options?.isCompleteSeries) params.append('is_complete_series', 'true');
    if (options?.isFinalEpisode) params.append('is_final_episode', 'true');
    if (options?.episodeOnly) params.append('episode_only', 'true');
    if (options?.edition) params.append('edition', options.edition);
    if (options?.info) params.append('info', options.info);
    if (options?.language !== undefined) params.append('language', options.language);
    
    const response = await api.post(`/tmdb/generate-name?${params}`, mediaInfo);
    return response.data;
  },

  detectEpisode: async (filename: string): Promise<{
    is_series: boolean;
    season: number | null;
    episode: number | null;
    is_complete_season: boolean;
  }> => {
    const response = await api.get(`/tmdb/detect-episode?filename=${encodeURIComponent(filename)}`);
    return response.data;
  },

  extractTitle: async (filename: string): Promise<{
    original_filename: string;
    extracted_title: string;
  }> => {
    const response = await api.get(`/tmdb/extract-title?filename=${encodeURIComponent(filename)}`);
    return response.data;
  },

  searchFromFilename: async (filename: string, type: 'movie' | 'tv' = 'movie'): Promise<{
    original_filename: string;
    extracted_title: string;
    results: TMDBSearchResult[];
  }> => {
    const params = new URLSearchParams({ filename, type });
    const response = await api.get(`/tmdb/search-from-filename?${params}`);
    return response.data;
  },
};

export const lacaleApi = {
  upload: async (data: LaCaleUploadRequest): Promise<LaCaleUploadResponse> => {
    const response = await api.post<LaCaleUploadResponse>('/lacale/upload', data);
    return response.data;
  },
};

export default api;
