/**
 * Utilitaires de formatage partagés
 */

import type { AudioTrack, SubtitleTrack } from '../types';

/**
 * Formate une taille en bytes en format lisible (KB, MB, GB, etc.)
 */
export const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

/**
 * Formate une durée en secondes en format lisible (Xh Xm Xs)
 */
export const formatDuration = (seconds: number | null): string => {
  if (seconds === null || seconds === undefined) return 'N/A';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return h > 0 ? `${h}h ${m}m ${s}s` : `${m}m ${s}s`;
};

/**
 * Détermine la résolution standard à partir de la largeur en pixels
 * 
 * Règles:
 * - width >= 3840 : 2160p (4K)
 * - width >= 1920 : 1080p (Full HD)
 * - width >= 1280 : 720p (HD)
 * - width >= 1024 : 576p (SD)
 * - width >= 720  : 480p (SD)
 * - sinon         : {width}p
 */
export const getResolutionFromWidth = (width: number | null | undefined): string => {
  if (!width) return 'Unknown';
  if (width >= 3840) return '2160p';
  if (width >= 1920) return '1080p';
  if (width >= 1280) return '720p';
  if (width >= 1024) return '576p';
  if (width >= 720) return '480p';
  return `${width}p`;
};

const LANGUAGE_LABELS: Record<string, string> = {
  fr: 'Français',
  fra: 'Français',
  fre: 'Français',
  french: 'Français',
  en: 'Anglais',
  eng: 'Anglais',
  english: 'Anglais',
  it: 'Italien',
  ita: 'Italien',
  italian: 'Italien',
  es: 'Espagnol',
  spa: 'Espagnol',
  spanish: 'Espagnol',
  de: 'Allemand',
  deu: 'Allemand',
  ger: 'Allemand',
  german: 'Allemand',
  ja: 'Japonais',
  jpn: 'Japonais',
  japanese: 'Japonais',
};

const normalizeLanguage = (value: string | null | undefined): string => {
  return (value || '').trim().toLowerCase();
};

const getLanguageLabel = (value: string | null | undefined): string => {
  const normalized = normalizeLanguage(value);
  if (!normalized) return 'Inconnue';
  return LANGUAGE_LABELS[normalized] || value || 'Inconnue';
};

const detectFrenchVariant = (
  releaseName: string | null | undefined,
  audioTracks: AudioTrack[]
): 'VFF' | 'VFQ' | 'VFI' | null => {
  const release = (releaseName || '').toUpperCase();
  const titles = audioTracks.map((track) => (track.title || '').toUpperCase()).join(' ');
  const source = `${release} ${titles}`;

  if (source.includes('TRUEFRENCH') || source.includes('VFF')) return 'VFF';
  if (source.includes('VFQ')) return 'VFQ';
  if (source.includes('VFI')) return 'VFI';
  return null;
};

export const formatAudioLanguages = (
  audioTracks: AudioTrack[] | null | undefined,
  releaseName?: string | null
): string => {
  if (!audioTracks || audioTracks.length === 0) return 'Inconnue';

  const frenchVariant = detectFrenchVariant(releaseName, audioTracks);
  const labels: string[] = [];

  for (const track of audioTracks) {
    const normalized = normalizeLanguage(track.language);
    let label = getLanguageLabel(track.language);

    if ((normalized === 'fr' || normalized === 'fra' || normalized === 'fre' || normalized === 'french') && frenchVariant) {
      label = `Français (${frenchVariant})`;
    }

    if (!labels.includes(label)) {
      labels.push(label);
    }
  }

  return labels.length > 0 ? labels.join(', ') : 'Inconnue';
};

export const formatSubtitleLanguages = (
  subtitleTracks: SubtitleTrack[] | null | undefined
): string => {
  if (!subtitleTracks || subtitleTracks.length === 0) return 'Aucun';

  const labels: string[] = [];

  for (const track of subtitleTracks) {
    const title = (track.title || '').toLowerCase();
    const isForced = Boolean(track.forced) || title.includes('forced') || title.includes('force');
    const base = getLanguageLabel(track.language);
    const label = isForced ? `${base} (forcé)` : base;

    if (!labels.includes(label)) {
      labels.push(label);
    }
  }

  return labels.length > 0 ? labels.join(', ') : 'Aucun';
};
