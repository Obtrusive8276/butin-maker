/**
 * Utilitaires de formatage partagés
 */

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
