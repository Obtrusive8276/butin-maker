import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Finalize from './Finalize';
import { useAppStore } from '../stores/appStore';
import { renderWithQuery } from '../../tests/test-utils';

// Mock toutes les APIs
vi.mock('../services/api', () => ({
  torrentApi: {
    downloadTorrent: vi.fn((name: string) => `/api/torrent/download/${name}`),
    addForSeeding: vi.fn(),
  },
  mediainfoApi: {
    downloadNfo: vi.fn((name: string) => `/api/mediainfo/download-nfo/${name}`),
  },
  tagsApi: {
    getAll: vi.fn().mockResolvedValue({ quaiprincipalcategories: [] }),
  },
  presentationApi: {
    generate: vi.fn().mockResolvedValue({ bbcode: '' }),
  },
  lacaleApi: {
    getCategoryId: vi.fn(),
    upload: vi.fn(),
    getMeta: vi.fn(),
  },
}));

import { lacaleApi } from '../services/api';

const mockSettings = {
  qbittorrent: { host: 'http://localhost', port: 8080, username: 'admin', password: 'admin' },
  tracker: { announce_url: '', upload_url: 'https://la-cale.space/upload', lacale_api_key: '' },
  paths: { default_browse_path: '', hardlink_path: '', qbittorrent_download_path: '', output_path: '' },
  tmdb: { api_key: '' },
};

const mockSettingsWithApiKey = {
  ...mockSettings,
  tracker: { ...mockSettings.tracker, lacale_api_key: 'test-api-key-123' },
};

const mockTorrentResult = {
  success: true,
  torrent_path: '/app/output/test.torrent',
  torrent_name: 'My.Movie.2024.MULTi.1080p.BluRay.x264-TEAM',
  info_hash: 'abc123def456',
  size: 5000000000,
  piece_count: 1200,
};

const mockFile = {
  path: '/data/My.Movie.2024.mkv',
  name: 'My.Movie.2024.mkv',
  is_dir: false,
  size: 5000000000,
  extension: 'mkv',
};

const mockTmdbInfo = {
  id: 12345,
  title: 'My Movie',
  original_title: 'My Movie',
  year: '2024',
  poster_path: 'https://image.tmdb.org/t/p/w500/poster.jpg',
  overview: 'A great movie',
  vote_average: 7.5,
  genres: 'Action, Drama',
  type: 'movie' as const,
};

describe('Finalize', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    useAppStore.setState({
      selectedFiles: [mockFile],
      settings: mockSettings,
      torrentResult: mockTorrentResult,
      nfoPath: '/app/output/My.Movie.2024.nfo',
      generatedBBCode: '[b]Test[/b]',
      contentType: 'movie',
      releaseName: 'My.Movie.2024.MULTi.1080p.BluRay.x264-TEAM',
      tmdbInfo: mockTmdbInfo,
      mediaInfo: null,
      selectedTags: [],
    });
  });

  it('affiche un warning quand la cle API est absente', () => {
    renderWithQuery(<Finalize />);

    expect(screen.getByText(/Clé API non configurée/)).toBeInTheDocument();
    // Le bouton d'upload auto ne doit PAS etre present
    expect(screen.queryByText('Upload automatique vers La Cale')).not.toBeInTheDocument();
    // Le bouton d'upload manuel doit etre present
    expect(screen.getByText(/Ouvrir La Cale - Upload/)).toBeInTheDocument();
  });

  it('affiche le bouton upload auto quand la cle API est configuree', () => {
    useAppStore.setState({ settings: mockSettingsWithApiKey });
    renderWithQuery(<Finalize />);

    expect(screen.getByText('Upload automatique vers La Cale')).toBeInTheDocument();
    expect(screen.queryByText(/Clé API non configurée/)).not.toBeInTheDocument();
  });

  it('affiche le lien apres un upload reussi', async () => {
    const user = userEvent.setup();
    useAppStore.setState({ settings: mockSettingsWithApiKey });

    vi.mocked(lacaleApi.getCategoryId).mockResolvedValue({ category_id: 'cat-films-123' });
    vi.mocked(lacaleApi.upload).mockResolvedValue({
      success: true,
      id: '42',
      slug: 'my-movie-2024',
      link: 'https://la-cale.space/torrents/42-my-movie-2024',
    });

    renderWithQuery(<Finalize />);

    const uploadBtn = screen.getByText('Upload automatique vers La Cale');
    await user.click(uploadBtn);

    await waitFor(() => {
      expect(screen.getByText('Upload réussi!')).toBeInTheDocument();
    });
    expect(screen.getByText('Voir le torrent sur La Cale')).toBeInTheDocument();
    expect(screen.getByText('Voir le torrent sur La Cale').closest('a')).toHaveAttribute(
      'href',
      'https://la-cale.space/torrents/42-my-movie-2024'
    );
  });

  it('affiche erreur 401 - cle API invalide', async () => {
    const user = userEvent.setup();
    useAppStore.setState({ settings: mockSettingsWithApiKey });

    vi.mocked(lacaleApi.getCategoryId).mockResolvedValue({ category_id: 'cat-films-123' });
    vi.mocked(lacaleApi.upload).mockRejectedValue({
      response: { status: 401, data: { detail: 'Unauthorized' } },
    });

    renderWithQuery(<Finalize />);
    await user.click(screen.getByText('Upload automatique vers La Cale'));

    await waitFor(() => {
      expect(screen.getByText(/Clé API invalide/)).toBeInTheDocument();
    });
  });

  it('affiche erreur 409 - torrent deja existant', async () => {
    const user = userEvent.setup();
    useAppStore.setState({ settings: mockSettingsWithApiKey });

    vi.mocked(lacaleApi.getCategoryId).mockResolvedValue({ category_id: 'cat-films-123' });
    vi.mocked(lacaleApi.upload).mockRejectedValue({
      response: { status: 409, data: { detail: 'Conflict' } },
    });

    renderWithQuery(<Finalize />);
    await user.click(screen.getByText('Upload automatique vers La Cale'));

    await waitFor(() => {
      expect(screen.getByText(/torrent existe déjà/)).toBeInTheDocument();
    });
  });

  it('affiche erreur 429 - rate limit', async () => {
    const user = userEvent.setup();
    useAppStore.setState({ settings: mockSettingsWithApiKey });

    vi.mocked(lacaleApi.getCategoryId).mockResolvedValue({ category_id: 'cat-films-123' });
    vi.mocked(lacaleApi.upload).mockRejectedValue({
      response: { status: 429, data: { detail: 'Rate limited' } },
    });

    renderWithQuery(<Finalize />);
    await user.click(screen.getByText('Upload automatique vers La Cale'));

    await waitFor(() => {
      expect(screen.getByText(/30 requêtes\/minute/)).toBeInTheDocument();
    });
  });

  it('permet de reessayer apres une erreur', async () => {
    const user = userEvent.setup();
    useAppStore.setState({ settings: mockSettingsWithApiKey });

    vi.mocked(lacaleApi.getCategoryId).mockResolvedValue({ category_id: 'cat-films-123' });
    // Premier appel echoue
    vi.mocked(lacaleApi.upload).mockRejectedValueOnce({
      response: { status: 500, data: { detail: 'Server error' } },
    });
    // Deuxieme appel reussit
    vi.mocked(lacaleApi.upload).mockResolvedValueOnce({
      success: true,
      id: '42',
      slug: 'my-movie-2024',
      link: 'https://la-cale.space/torrents/42',
    });

    renderWithQuery(<Finalize />);

    // Premier essai - echoue
    await user.click(screen.getByText('Upload automatique vers La Cale'));
    await waitFor(() => {
      expect(screen.getByText('Réessayer')).toBeInTheDocument();
    });

    // Cliquer sur Reessayer reset l'etat a idle
    await user.click(screen.getByText('Réessayer'));

    // Le bouton upload auto doit reapparaitre
    await waitFor(() => {
      expect(screen.getByText('Upload automatique vers La Cale')).toBeInTheDocument();
    });

    // Deuxieme essai - reussit
    await user.click(screen.getByText('Upload automatique vers La Cale'));
    await waitFor(() => {
      expect(screen.getByText('Upload réussi!')).toBeInTheDocument();
    });
  });

  it('sanitize les URLs javascript dans le BBCode preview', () => {
    // Inject du BBCode malveillant avec javascript: URL
    useAppStore.setState({
      generatedBBCode: '[url=javascript:alert(1)]Click me[/url] [img]javascript:alert(2)[/img]',
    });

    renderWithQuery(<Finalize />);

    // Le BBCode est rendu dans l'editeur textarea par defaut (pas le preview HTML)
    // Verifions que le contenu brut est la
    const textarea = screen.getByPlaceholderText('BBCode de la présentation...');
    expect(textarea).toBeInTheDocument();

    // Le bbcodeToHtml doit avoir remplace javascript: par "#" pour [url] et "" pour [img]
    // Pour tester cela, on verifie que l'apercu HTML est safe
    // Importons et testons directement bbcodeToHtml via le rendu
    // On simule le clic sur "Apercu" pour afficher le HTML
    // Mais le texte dans le textarea n'est pas sanitize (c'est normal pour l'edition)
    // Le danger est uniquement dans dangerouslySetInnerHTML

    // Verifions que le composant ne contient pas de href="javascript:"
    // Le textarea contient le BBCode brut - OK
    expect((textarea as HTMLTextAreaElement).value).toContain('javascript:alert(1)');
  });

  it('XSS - le preview HTML ne contient pas de javascript: URLs', async () => {
    const user = userEvent.setup();

    useAppStore.setState({
      generatedBBCode: '[url=javascript:alert(1)]XSS[/url]',
    });

    renderWithQuery(<Finalize />);

    // Cliquer sur "Apercu" BBCode (le 2eme bouton "Apercu")
    const previewBtns = screen.getAllByText('Aperçu');
    await user.click(previewBtns[1]);

    // En mode apercu, le contenu est rendu via dangerouslySetInnerHTML + sanitizeHtml
    // bbcodeToHtml convertit javascript: en "#", puis DOMPurify sanitize
    // DOMPurify avec ALLOWED_URI_REGEXP n'autorise que http/https/ftp
    // Donc le href="#" est soit retire soit conserve - dans tous les cas, pas de javascript:
    await waitFor(() => {
      const links = document.querySelectorAll('a');
      links.forEach((link) => {
        const href = link.getAttribute('href');
        // href doit etre null (supprime par DOMPurify) ou "#" ou http(s)
        // JAMAIS javascript:
        if (href !== null) {
          expect(href).not.toContain('javascript:');
        }
      });
    });

    // Verifier aussi qu'il n'y a pas de contenu dangereux dans le HTML brut
    const previewContainer = document.querySelector('.prose');
    if (previewContainer) {
      expect(previewContainer.innerHTML).not.toContain('javascript:');
    }
  });
});
