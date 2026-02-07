import { useQuery } from '@tanstack/react-query';
import { lacaleApi } from '../services/api';
import type { LaCaleMetaResponse } from '../types';
import { FALLBACK_META_DATA } from '../utils/tagsDataFallback';
import axios from 'axios';

const CACHE_KEY = 'lacale_meta_cache';
const STALE_TIME = 60 * 60 * 1000; // 1 heure
const LOCAL_STORAGE_TTL = 24 * 60 * 60 * 1000; // 24 heures

interface CachedMeta extends LaCaleMetaResponse {
  _cachedAt: number;
}

function loadFromLocalStorage(): LaCaleMetaResponse | null {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const parsed: CachedMeta = JSON.parse(raw);
    if (parsed._cachedAt && Date.now() - parsed._cachedAt > LOCAL_STORAGE_TTL) {
      localStorage.removeItem(CACHE_KEY);
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

function saveToLocalStorage(data: LaCaleMetaResponse): void {
  try {
    const cached: CachedMeta = {
      ...data,
      _cachedAt: Date.now(),
    };
    localStorage.setItem(CACHE_KEY, JSON.stringify(cached));
  } catch {
    // localStorage plein ou indisponible — on ignore silencieusement
  }
}

/**
 * Hook pour charger les métadonnées (catégories + tags) depuis l'API La Cale.
 * - Cache TanStack Query avec staleTime de 1h
 * - Fallback localStorage si l'API est indisponible
 * - Fallback ultime : données locales (FALLBACK_META_DATA)
 * - Persiste en localStorage pour 24h
 */
export function useCachedTags() {
  return useQuery<LaCaleMetaResponse>({
    queryKey: ['lacale-meta'],
    queryFn: async () => {
      const data = await lacaleApi.getMeta();
      saveToLocalStorage(data);
      return data;
    },
    staleTime: STALE_TIME,
    placeholderData: () => loadFromLocalStorage() ?? FALLBACK_META_DATA,
    retry: (failureCount, error) => {
      // Ne jamais retry sur 429 (rate limit) — cela aggraverait le problème
      if (axios.isAxiosError(error) && error.response?.status === 429) {
        return false;
      }
      // 1 retry max pour les autres erreurs
      return failureCount < 1;
    },
    retryDelay: 5000, // 5s entre les retries
  });
}
