import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RenameEditor from './RenameEditor';
import { useAppStore } from '../stores/appStore';
import { renderWithQuery } from '../../tests/test-utils';

// Mock l'API
vi.mock('../services/api', () => ({
  tmdbApi: {
    generateReleaseName: vi.fn(),
  },
  mediainfoApi: {
    generateNfo: vi.fn(),
  },
}));

import { tmdbApi, mediainfoApi } from '../services/api';

const mockFile = {
  path: '/data/My.Movie.2024.mkv',
  name: 'My.Movie.2024.mkv',
  is_dir: false,
  size: 5000000000,
  extension: 'mkv',
};

const mockMediaInfo = {
  file_path: '/data/My.Movie.2024.mkv',
  file_name: 'My.Movie.2024.mkv',
  file_size: 5000000000,
  container: 'Matroska',
  duration: 7200,
  video_tracks: [{ codec: 'AVC', width: 1920, height: 1080, bitrate: null, framerate: 23.976, duration: 7200, hdr: null }],
  audio_tracks: [{ codec: 'AAC', channels: 6, bitrate: null, language: 'fra', title: null }],
  subtitle_tracks: [],
};

const mockTmdbInfo = {
  id: 12345,
  title: 'My Movie',
  original_title: 'My Movie',
  year: '2024',
  poster_path: '/poster.jpg',
  overview: 'A test movie',
  vote_average: 7.5,
  genres: 'Action, Drama',
  type: 'movie' as const,
};

const mockSettings = {
  qbittorrent: { host: 'http://localhost', port: 8080, username: 'admin', password: 'admin' },
  tracker: { announce_url: '', upload_url: '', lacale_api_key: '' },
  paths: { default_browse_path: '', hardlink_path: '/mnt/hardlinks', qbittorrent_download_path: '', output_path: '' },
  tmdb: { api_key: '' },
};

describe('RenameEditor', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Setup le store avec des donnees valides
    useAppStore.setState({
      selectedFiles: [mockFile],
      mediaInfo: mockMediaInfo,
      tmdbInfo: mockTmdbInfo,
      contentType: 'movie',
      seriesInfo: { season: null, episode: null, isCompleteSeason: false },
      releaseName: '',
      settings: mockSettings,
      mediaInfoFilePath: '/data/My.Movie.2024.mkv',
      nfoPath: null,
    });

    // Mock par defaut: generateReleaseName retourne un nom valide
    vi.mocked(tmdbApi.generateReleaseName).mockResolvedValue({
      release_name: 'My.Movie.2024.MULTi.1080p.BluRay.x264-TEAM',
    });

    vi.mocked(mediainfoApi.generateNfo).mockResolvedValue({
      success: true,
      file_path: '/app/output/My.Movie.2024.MULTi.1080p.BluRay.x264-TEAM.nfo',
    });
  });

  it('genere automatiquement un nom au premier montage (pas de boucle infinie)', async () => {
    renderWithQuery(<RenameEditor />);

    // Attendre que la mutation soit appelee
    await waitFor(() => {
      expect(tmdbApi.generateReleaseName).toHaveBeenCalled();
    });

    // La mutation doit etre appelee exactement 1 fois (pas de boucle)
    expect(tmdbApi.generateReleaseName).toHaveBeenCalledTimes(1);

    // Le nom de release doit apparaitre dans le store
    await waitFor(() => {
      expect(useAppStore.getState().releaseName).toBe('My.Movie.2024.MULTi.1080p.BluRay.x264-TEAM');
    });
  });

  it('regenere automatiquement quand une option change', async () => {
    const user = userEvent.setup();

    renderWithQuery(<RenameEditor />);

    // Attendre la generation initiale
    await waitFor(() => {
      expect(tmdbApi.generateReleaseName).toHaveBeenCalledTimes(1);
    });

    // Changer la source via le select (label sans htmlFor, on cherche par texte dans le container)
    const sourceLabel = screen.getByText('Source');
    const sourceSelect = sourceLabel.closest('div')!.querySelector('select')!;
    await user.selectOptions(sourceSelect, 'BluRay');

    // La mutation doit etre re-appelee
    await waitFor(() => {
      expect(tmdbApi.generateReleaseName).toHaveBeenCalledTimes(2);
    });
  });

  it('utilise hardlink_path des settings (pas /data/ hardcode)', async () => {
    renderWithQuery(<RenameEditor />);

    // Attendre que la mutation succeed et le hardlink path soit set
    await waitFor(() => {
      expect(useAppStore.getState().releaseName).toBe('My.Movie.2024.MULTi.1080p.BluRay.x264-TEAM');
    });

    // Le hardlink doit utiliser le path des settings, pas "/data/"
    const destinationText = screen.getByText((content) =>
      content.includes('/mnt/hardlinks/My.Movie.2024.MULTi.1080p.BluRay.x264-TEAM.mkv')
    );
    expect(destinationText).toBeInTheDocument();
  });

  it('ne fait pas de mutation si mediaInfo ou tmdbInfo est null', async () => {
    // Override le store sans mediaInfo
    useAppStore.setState({
      mediaInfo: null,
      tmdbInfo: null,
    });

    renderWithQuery(<RenameEditor />);

    // Attendre un tick pour laisser les effets se propager
    await new Promise((r) => setTimeout(r, 100));

    // La mutation ne doit PAS etre appelee
    expect(tmdbApi.generateReleaseName).not.toHaveBeenCalled();
  });

  it('permet la modification manuelle du nom de release', async () => {
    const user = userEvent.setup();

    renderWithQuery(<RenameEditor />);

    // Attendre la generation initiale
    await waitFor(() => {
      expect(useAppStore.getState().releaseName).toBe('My.Movie.2024.MULTi.1080p.BluRay.x264-TEAM');
    });

    // Trouver l'input et le modifier
    const input = screen.getByPlaceholderText('Nom de release...');
    await user.clear(input);
    await user.type(input, 'Custom.Name.2024');

    // Le store doit refleter le changement
    expect(useAppStore.getState().releaseName).toBe('Custom.Name.2024');
  });
});
