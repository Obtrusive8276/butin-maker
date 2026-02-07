import { describe, it, expect } from 'vitest';
import type { ReactNode } from 'react';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCachedTags } from './useCachedTags';
import { FALLBACK_META_DATA } from '../utils/tagsDataFallback';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe('useCachedTags', () => {
  it('retourne les tags locaux sans appel reseau', () => {
    const { result } = renderHook(() => useCachedTags(), {
      wrapper: createWrapper(),
    });

    expect(result.current.data).toEqual(FALLBACK_META_DATA);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isError).toBe(false);
  });
});
