import type { LaCaleMetaResponse, LaCaleTag, LaCaleTagGroup } from '../types';
import { FALLBACK_META_DATA } from './tagsDataFallback';

const CATEGORY_SLUG_MAP: Record<string, string> = {
  movie: 'films',
  tv: 'series',
};

export interface AdaptedTag {
  id: string;      // ID API La Cale (pour l'upload)
  name: string;    // Nom affiché
  slug: string;    // Slug
}

export interface AdaptedTagGroup {
  name: string;         // Nom du groupe (ex: "Qualité vidéo")
  tags: AdaptedTag[];   // Tags du groupe
}

/**
 * Pour un tagGroup API dont les tags sont null/vides, cherche un fallback
 * correspondant par slug ou nom (insensible à la casse).
 */
function findFallbackGroup(apiGroup: LaCaleTagGroup): LaCaleTagGroup | null {
  const slugLower = apiGroup.slug?.toLowerCase();
  const nameLower = apiGroup.name?.toLowerCase();

  for (const fb of FALLBACK_META_DATA.tagGroups ?? []) {
    if (
      (slugLower && fb.slug?.toLowerCase() === slugLower) ||
      (nameLower && fb.name?.toLowerCase() === nameLower)
    ) {
      return fb;
    }
  }
  return null;
}

/**
 * Filtre les tags par catégorie (films ou séries).
 * Les tags sans annotation `categories` passent toujours (compatibilité API).
 */
function filterTagsByCategory(tags: LaCaleTag[], categorySlug: string): LaCaleTag[] {
  return tags.filter(
    (t) => !t.categories || t.categories.length === 0 || t.categories.includes(categorySlug)
  );
}

/**
 * Transforme la réponse /meta en groupes de tags exploitables par Finalize.
 * - Fusionne avec les données fallback locales quand l'API retourne tags:null
 * - Filtre par catégorie (films/séries) si contentType est fourni
 *
 * @param meta - Réponse brute de /api/external/meta
 * @param contentType - "movie" ou "tv" (optionnel, pour filtrer par catégorie)
 */
export function adaptMetaToTagGroups(meta: LaCaleMetaResponse, contentType?: string): AdaptedTagGroup[] {
  const groups: AdaptedTagGroup[] = [];
  const categorySlug = contentType ? CATEGORY_SLUG_MAP[contentType] : null;

  // Collecter les slugs des groupes API pour détecter les groupes fallback manquants
  const apiGroupSlugs = new Set(
    (meta.tagGroups ?? []).map((tg) => tg.slug?.toLowerCase()).filter(Boolean)
  );

  // 1. Parcourir les groupes API, avec fallback si tags null/vide
  for (const tg of meta.tagGroups ?? []) {
    let tags: LaCaleTag[] = tg.tags ?? [];

    // Si le groupe API a des tags null/vides, utiliser le fallback local
    if (tags.length === 0) {
      const fallback = findFallbackGroup(tg);
      if (fallback) {
        tags = fallback.tags ?? [];
      }
    }

    // Filtrer par catégorie si demandé
    if (categorySlug) {
      tags = filterTagsByCategory(tags, categorySlug);
    }

    if (tags.length > 0) {
      groups.push({
        name: tg.name,
        tags: tags.map((t) => ({ id: t.id, name: t.name, slug: t.slug })),
      });
    }
  }

  // 2. Ajouter les groupes fallback qui n'existent pas du tout dans l'API
  for (const fb of FALLBACK_META_DATA.tagGroups ?? []) {
    const fbSlug = fb.slug?.toLowerCase();
    if (fbSlug && !apiGroupSlugs.has(fbSlug)) {
      let tags: LaCaleTag[] = fb.tags ?? [];
      if (categorySlug) {
        tags = filterTagsByCategory(tags, categorySlug);
      }
      if (tags.length > 0) {
        groups.push({
          name: fb.name,
          tags: tags.map((t) => ({ id: t.id, name: t.name, slug: t.slug })),
        });
      }
    }
  }

  // 3. Ungrouped tags
  if (meta.ungroupedTags?.length) {
    let ungrouped: LaCaleTag[] = meta.ungroupedTags;
    if (categorySlug) {
      ungrouped = filterTagsByCategory(ungrouped, categorySlug);
    }
    if (ungrouped.length > 0) {
      groups.push({
        name: 'Autres',
        tags: ungrouped.map((t: LaCaleTag) => ({
          id: t.id,
          name: t.name,
          slug: t.slug,
        })),
      });
    }
  }

  return groups;
}

/**
 * Cherche un tag par nom ou slug (insensible à la casse) et retourne son ID.
 * Utilisé pour la présélection automatique des tags.
 */
export function findTagId(groups: AdaptedTagGroup[], nameOrSlug: string): string | null {
  const lower = nameOrSlug.toLowerCase();
  for (const group of groups) {
    const found = group.tags.find(
      (t) => t.name.toLowerCase() === lower || t.slug.toLowerCase() === lower
    );
    if (found) return found.id;
  }
  return null;
}

/**
 * Trouve l'ID de catégorie La Cale à partir du type de contenu.
 * Port de la logique backend find_category_id() pour éviter un appel API supplémentaire.
 *
 * @param meta - Réponse /meta déjà chargée
 * @param contentType - "movie" ou "tv"
 * @returns ID de la catégorie (ex: "cmjoyv2cd00027eryreyk39gz") ou null
 */
export function findCategoryId(meta: LaCaleMetaResponse, contentType: string): string | null {
  const targetSlug = CATEGORY_SLUG_MAP[contentType];
  if (!targetSlug) return null;

  for (const category of meta.categories ?? []) {
    // Chercher dans les enfants (structure hiérarchique)
    for (const child of category.children ?? []) {
      if (child.slug === targetSlug) return child.id;
    }
    // Chercher aussi au niveau racine
    if (category.slug === targetSlug) return category.id;
  }

  return null;
}
