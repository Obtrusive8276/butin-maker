import type { LaCaleMetaResponse, LaCaleTag } from '../types';

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
 * Transforme la réponse /meta en groupes de tags exploitables par Finalize.
 * tagGroups[] → AdaptedTagGroup[] + ungroupedTags → groupe "Autres"
 */
export function adaptMetaToTagGroups(meta: LaCaleMetaResponse): AdaptedTagGroup[] {
  const groups: AdaptedTagGroup[] = [];

  for (const tg of meta.tagGroups ?? []) {
    groups.push({
      name: tg.name,
      tags: (tg.tags ?? []).map((t: LaCaleTag) => ({
        id: t.id,
        name: t.name,
        slug: t.slug,
      })),
    });
  }

  if (meta.ungroupedTags?.length) {
    groups.push({
      name: 'Autres',
      tags: meta.ungroupedTags.map((t: LaCaleTag) => ({
        id: t.id,
        name: t.name,
        slug: t.slug,
      })),
    });
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
