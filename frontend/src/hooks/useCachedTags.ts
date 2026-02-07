import { useQuery } from '@tanstack/react-query';
import type { LaCaleMetaResponse } from '../types';
import { FALLBACK_META_DATA } from '../utils/tagsDataFallback';

const TAGS_QUERY_KEY = ['lacale-tags-local'];

/**
 * Hook tags local-only.
 *
 * Décision produit: ne plus appeler /lacale/meta côté frontend tant que
 * l'API retourne des groupes vidéo incomplets (tags:null).
 *
 * Les tags proviennent uniquement de tagsDataFallback.ts.
 */
export function useCachedTags() {
  return useQuery<LaCaleMetaResponse>({
    queryKey: TAGS_QUERY_KEY,
    queryFn: async () => FALLBACK_META_DATA,
    staleTime: Number.POSITIVE_INFINITY,
    gcTime: Number.POSITIVE_INFINITY,
    retry: false,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    initialData: FALLBACK_META_DATA,
  });
}
