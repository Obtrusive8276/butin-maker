import { describe, it, expect } from 'vitest';
import { formatSize, formatDuration, getResolutionFromWidth } from './format';

describe('formatSize', () => {
  it('retourne "0 B" pour 0 bytes', () => {
    expect(formatSize(0)).toBe('0 B');
  });

  it('formate correctement les tailles standards', () => {
    expect(formatSize(1024)).toBe('1 KB');
    expect(formatSize(1048576)).toBe('1 MB');
    expect(formatSize(1073741824)).toBe('1 GB');
    expect(formatSize(5368709120)).toBe('5 GB');
  });

  it('arrondit a 2 decimales', () => {
    expect(formatSize(1536)).toBe('1.5 KB');
    expect(formatSize(2621440)).toBe('2.5 MB');
  });
});

describe('formatDuration', () => {
  it('retourne "N/A" pour null et undefined', () => {
    expect(formatDuration(null)).toBe('N/A');
    expect(formatDuration(undefined as unknown as null)).toBe('N/A');
  });

  it('formate 0 secondes correctement (pas "N/A")', () => {
    // Bug identifie dans code review: !0 === true donc retournait "N/A"
    expect(formatDuration(0)).toBe('0m 0s');
  });

  it('formate des durees courtes', () => {
    expect(formatDuration(90)).toBe('1m 30s');
    expect(formatDuration(45)).toBe('0m 45s');
  });

  it('formate des durees longues avec heures', () => {
    expect(formatDuration(3600)).toBe('1h 0m 0s');
    expect(formatDuration(3661)).toBe('1h 1m 1s');
    expect(formatDuration(7384)).toBe('2h 3m 4s');
  });
});

describe('getResolutionFromWidth', () => {
  it('detecte les resolutions standards', () => {
    expect(getResolutionFromWidth(3840)).toBe('2160p');
    expect(getResolutionFromWidth(1920)).toBe('1080p');
    expect(getResolutionFromWidth(1280)).toBe('720p');
    expect(getResolutionFromWidth(1024)).toBe('576p');
    expect(getResolutionFromWidth(720)).toBe('480p');
  });

  it('retourne "Unknown" pour null et undefined', () => {
    expect(getResolutionFromWidth(null)).toBe('Unknown');
    expect(getResolutionFromWidth(undefined)).toBe('Unknown');
  });

  it('gere les resolutions scope (ex: 1920x816 reste 1080p)', () => {
    // Un film scope a 1920 de large mais ~800 de haut
    // La detection se fait sur la largeur uniquement
    expect(getResolutionFromWidth(1920)).toBe('1080p');
  });

  it('gere les resolutions au-dessus de 4K', () => {
    expect(getResolutionFromWidth(7680)).toBe('2160p'); // 8K -> tombe dans >= 3840
  });

  it('gere les petites resolutions non-standard', () => {
    expect(getResolutionFromWidth(640)).toBe('640p');
    expect(getResolutionFromWidth(320)).toBe('320p');
  });
});
