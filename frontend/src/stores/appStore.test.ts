import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAppStore } from './appStore';

describe('appStore', () => {
  beforeEach(() => {
    // Reset complet du store avant chaque test
    const { getState } = useAppStore;
    act(() => {
      useAppStore.setState({
        currentStep: 'files',
        selectedFiles: [],
        releaseName: '',
        lacaleUploadStatus: 'idle',
        lacaleUploadResult: null,
        lacaleUploadError: null,
        selectedTags: [],
        presentationData: {
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
        },
      }, false);
    });
  });

  it('setReleaseName met a jour correctement', () => {
    const { result } = renderHook(() => useAppStore());

    act(() => {
      result.current.setReleaseName('New.Release.Name.2024');
    });

    expect(result.current.releaseName).toBe('New.Release.Name.2024');
  });

  it('setLaCaleUploadStatus gere les transitions', () => {
    const { result } = renderHook(() => useAppStore());

    expect(result.current.lacaleUploadStatus).toBe('idle');

    act(() => result.current.setLaCaleUploadStatus('loading'));
    expect(result.current.lacaleUploadStatus).toBe('loading');

    act(() => result.current.setLaCaleUploadStatus('success'));
    expect(result.current.lacaleUploadStatus).toBe('success');

    act(() => result.current.setLaCaleUploadStatus('error'));
    expect(result.current.lacaleUploadStatus).toBe('error');

    act(() => result.current.setLaCaleUploadStatus('idle'));
    expect(result.current.lacaleUploadStatus).toBe('idle');
  });

  it('toggleTag ajoute et retire des tags', () => {
    const { result } = renderHook(() => useAppStore());

    expect(result.current.selectedTags).toHaveLength(0);

    act(() => result.current.toggleTag('1080p'));
    expect(result.current.selectedTags).toContain('1080p');

    act(() => result.current.toggleTag('MULTi'));
    expect(result.current.selectedTags).toEqual(['1080p', 'MULTi']);

    // Toggle off
    act(() => result.current.toggleTag('1080p'));
    expect(result.current.selectedTags).toEqual(['MULTi']);
  });

  it('clearSelectedFiles vide le tableau et addSelectedFile evite les doublons', () => {
    const { result } = renderHook(() => useAppStore());

    const file1 = { path: '/test1.mkv', name: 'test1.mkv', is_dir: false, size: 1000, extension: 'mkv' };
    const file2 = { path: '/test2.mkv', name: 'test2.mkv', is_dir: false, size: 2000, extension: 'mkv' };

    act(() => result.current.addSelectedFile(file1));
    act(() => result.current.addSelectedFile(file2));
    expect(result.current.selectedFiles).toHaveLength(2);

    // Doublon ignore
    act(() => result.current.addSelectedFile(file1));
    expect(result.current.selectedFiles).toHaveLength(2);

    act(() => result.current.clearSelectedFiles());
    expect(result.current.selectedFiles).toHaveLength(0);
  });

  it('setPresentationData merge partiellement', () => {
    const { result } = renderHook(() => useAppStore());

    act(() => {
      result.current.setPresentationData({
        title: 'Test Title',
        rating: '8.5',
      });
    });

    expect(result.current.presentationData.title).toBe('Test Title');
    expect(result.current.presentationData.rating).toBe('8.5');
    // Les autres champs restent vides
    expect(result.current.presentationData.genre).toBe('');

    act(() => result.current.resetPresentationData());
    expect(result.current.presentationData.title).toBe('');
    expect(result.current.presentationData.rating).toBe('');
  });
});
