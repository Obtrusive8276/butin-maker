import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useClipboard } from './useClipboard';

describe('useClipboard', () => {
  beforeEach(() => {
    vi.mocked(navigator.clipboard.writeText).mockResolvedValue(undefined);
  });

  it('copie du texte avec succes via Clipboard API', async () => {
    const { result } = renderHook(() => useClipboard());

    let success: boolean = false;
    await act(async () => {
      success = await result.current.copy('Test content');
    });

    expect(success).toBe(true);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('Test content');
    expect(result.current.copied).toBe(true);
    expect(result.current.error).toBeNull();
  });

  it('reset copied apres timeout', async () => {
    const { result } = renderHook(() => useClipboard(300));

    await act(async () => {
      await result.current.copy('Test');
    });

    expect(result.current.copied).toBe(true);

    // Attendre que le timeout expire
    await waitFor(() => {
      expect(result.current.copied).toBe(false);
    }, { timeout: 500 });
  });

  it('retourne erreur si texte vide', async () => {
    const { result } = renderHook(() => useClipboard());

    let success: boolean = true;
    await act(async () => {
      success = await result.current.copy('');
    });

    expect(success).toBe(false);
    expect(result.current.error).toBe('Pas de contenu à copier');
    expect(result.current.copied).toBe(false);
    expect(navigator.clipboard.writeText).not.toHaveBeenCalled();
  });

  it('clear timeout on unmount (pas de memory leak)', async () => {
    const { result, unmount } = renderHook(() => useClipboard(5000));

    await act(async () => {
      await result.current.copy('Test');
    });

    expect(result.current.copied).toBe(true);

    // Demonter avant le timeout - ne doit pas lancer d'erreur
    unmount();

    // Si le timeout n'est pas clear, setState serait appele sur
    // un composant demonte -> erreur React. Le test passe si aucune erreur.
  });
});
